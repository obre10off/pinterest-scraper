#!/usr/bin/env python3
"""
CLI Interface for TikTok Scraper
Command-line interface for managing profiles and running scraping operations.
"""

import click
import asyncio
import json
from pathlib import Path
from typing import List, Optional
from loguru import logger
from colorama import init, Fore, Style

from profile_manager import ProfileManager
from tiktok_scraper import TikTokScraper
from tiktok_scraper_selenium import TikTokScraperSelenium
from hook_analyzer import HookAnalyzer

# Initialize colorama for Windows compatibility
init(autoreset=True)


def print_header():
    """Print application header"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}🎵 TikTok Slideshow Scraper & Hook Analyzer")
    print(f"{Fore.CYAN}{'='*60}\n{Style.RESET_ALL}")


def print_success(message: str):
    """Print success message"""
    print(f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}")


def print_error(message: str):
    """Print error message"""
    print(f"{Fore.RED}❌ {message}{Style.RESET_ALL}")


def print_info(message: str):
    """Print info message"""
    print(f"{Fore.YELLOW}ℹ️  {message}{Style.RESET_ALL}")


def print_profile_table(profiles: List[dict]):
    """Print profiles in a formatted table"""
    if not profiles:
        print_info("No profiles found")
        return
    
    print(f"\n{Fore.CYAN}{'Username':<20} {'Status':<12} {'Posts':<10} {'Slideshows':<12} {'Errors':<8}{Style.RESET_ALL}")
    print("-" * 70)
    
    for profile in profiles:
        status_color = Fore.GREEN if profile['status'] == 'completed' else Fore.YELLOW if profile['status'] == 'pending' else Fore.RED
        print(f"@{profile['username']:<19} {status_color}{profile['status']:<12}{Style.RESET_ALL} "
              f"{profile['total_posts']:<10} {profile['slideshow_posts']:<12} {profile['errors']:<8}")


@click.group()
def cli():
    """TikTok Scraper CLI - Scrape slideshows and extract hooks from TikTok profiles"""
    print_header()


@cli.command()
@click.argument('usernames', nargs=-1, required=True)
def add(usernames):
    """Add TikTok profiles to scrape (without @ symbol or with)"""
    manager = ProfileManager()
    
    for username in usernames:
        success = manager.add_profile(username)
        if success:
            print_success(f"Added profile: @{username.strip().lstrip('@')}")
        else:
            print_info(f"Profile already exists: @{username.strip().lstrip('@')}")


@cli.command()
@click.argument('usernames', nargs=-1, required=True)
def remove(usernames):
    """Remove TikTok profiles from tracking"""
    manager = ProfileManager()
    
    for username in usernames:
        success = manager.remove_profile(username)
        if success:
            print_success(f"Removed profile: @{username.strip().lstrip('@')}")
        else:
            print_error(f"Profile not found: @{username.strip().lstrip('@')}")


@cli.command()
def list():
    """List all tracked profiles and their status"""
    manager = ProfileManager()
    profiles = manager.list_profiles()
    
    print(f"\n{Fore.CYAN}📊 Profile Summary{Style.RESET_ALL}")
    print_profile_table(profiles)
    
    # Summary statistics
    total = len(profiles)
    completed = sum(1 for p in profiles if p['status'] == 'completed')
    pending = sum(1 for p in profiles if p['status'] == 'pending')
    errors = sum(1 for p in profiles if p['status'] == 'error')
    
    print(f"\n{Fore.CYAN}Total: {total} | Completed: {completed} | Pending: {pending} | Errors: {errors}{Style.RESET_ALL}")


@cli.command()
@click.argument('username')
def info(username):
    """Get detailed information about a specific profile"""
    manager = ProfileManager()
    profile_info = manager.get_profile_info(username)
    
    if not profile_info:
        print_error(f"Profile @{username.strip().lstrip('@')} not found")
        return
    
    username = username.strip().lstrip('@')
    print(f"\n{Fore.CYAN}Profile: @{username}{Style.RESET_ALL}")
    print("-" * 40)
    
    for key, value in profile_info.items():
        if key != "metadata":
            print(f"{key}: {value}")
    
    # Check for scraped data
    output_dir = manager.get_profile_output_dir(username)
    if output_dir.exists():
        files = list(output_dir.iterdir())
        if files:
            print(f"\n{Fore.CYAN}Scraped Files:{Style.RESET_ALL}")
            for file in files:
                size = file.stat().st_size / 1024  # KB
                print(f"  - {file.name} ({size:.1f} KB)")


@cli.command()
@click.option('--profiles', '-p', multiple=True, help='Specific profiles to scrape')
@click.option('--all', 'scrape_all', is_flag=True, help='Scrape all pending profiles')
@click.option('--limit', '-l', type=int, help='Limit number of posts per profile')
@click.option('--headless', is_flag=True, help='Run browser in headless mode')
@click.option('--slideshows-only', is_flag=True, default=True, help='Only scrape slideshow posts')
@click.option('--use-selenium', is_flag=True, help='Use Selenium instead of Playwright')
def scrape(profiles, scrape_all, limit, headless, slideshows_only, use_selenium):
    """Scrape TikTok profiles for slideshow content"""
    manager = ProfileManager()
    
    # Determine which profiles to scrape
    if scrape_all:
        usernames = manager.get_pending_profiles()
        if not usernames:
            print_info("No pending profiles to scrape")
            return
    elif profiles:
        usernames = list(profiles)
    else:
        # Get pending profiles by default
        usernames = manager.get_pending_profiles()
        if not usernames:
            print_error("No profiles specified and no pending profiles found")
            print_info("Use --profiles to specify profiles or --all to scrape all pending")
            return
    
    print(f"\n{Fore.CYAN}🚀 Starting scraper...{Style.RESET_ALL}")
    print(f"Profiles to scrape: {', '.join(f'@{u.strip().lstrip('@')}' for u in usernames)}")
    
    # Update config if needed
    if limit:
        config_path = "config.json"
        with open(config_path, 'r') as f:
            config = json.load(f)
        config["scraper_settings"]["max_scrolls"] = min(limit // 10, 20)  # Rough estimate
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    # Run scraper
    if use_selenium:
        print_info("Using Selenium WebDriver...")
        try:
            scraper = TikTokScraperSelenium(headless=headless)
            results = scraper.scrape_multiple_profiles(usernames)
        except Exception as e:
            print_error(f"Selenium scraping failed: {e}")
            return
    else:
        print_info("Using Playwright (will fallback to Selenium if needed)...")
        async def run_scraper():
            try:
                scraper = TikTokScraper(headless=headless)
                results = await scraper.scrape_multiple_profiles(usernames)
                return results
            except Exception as e:
                print_error(f"Playwright failed: {e}")
                print_info("Falling back to Selenium...")
                selenium_scraper = TikTokScraperSelenium(headless=headless)
                return selenium_scraper.scrape_multiple_profiles(usernames)
        
        # Execute
        try:
            results = asyncio.run(run_scraper())
        except Exception as e:
            print_error(f"Scraping failed: {e}")
            logger.exception("Scraping error")
            return
    
    # Print summary
    print(f"\n{Fore.CYAN}📊 Scraping Summary{Style.RESET_ALL}")
    print("-" * 40)
    
    for result in results:
        username = result['username']
        if result.get('error'):
            print_error(f"@{username}: {result['error']}")
        else:
            print_success(f"@{username}: {result['total_posts']} posts, {result['slideshow_posts']} slideshows")


@cli.command()
@click.option('--output', '-o', default='training_dataset.json', help='Output file path')
@click.option('--data-dir', '-d', default='scraped_data', help='Directory with scraped data')
def analyze(output, data_dir):
    """Analyze scraped hooks and generate training dataset"""
    print(f"\n{Fore.CYAN}🔍 Analyzing hooks...{Style.RESET_ALL}")
    
    analyzer = HookAnalyzer()
    
    try:
        # Process scraped data
        training_data = analyzer.process_scraped_data(data_dir)
        
        if not training_data['hooks']:
            print_error("No hooks found in scraped data")
            return
        
        # Save training data
        analyzer.save_training_data(training_data, output)
        
        # Print analysis summary
        print(f"\n{Fore.CYAN}📊 Analysis Summary{Style.RESET_ALL}")
        print("-" * 40)
        print(f"Total hooks: {training_data['metadata']['total_hooks']}")
        print(f"Total posts: {training_data['metadata']['total_posts']}")
        
        print(f"\n{Fore.CYAN}Categories:{Style.RESET_ALL}")
        for category, count in training_data['metadata']['categories'].items():
            print(f"  - {category}: {count}")
        
        if training_data.get('statistics'):
            print(f"\n{Fore.CYAN}Statistics:{Style.RESET_ALL}")
            stats = training_data['statistics']
            print(f"  - Avg quality score: {stats['avg_quality_score']:.2f}")
            print(f"  - Avg hook length: {stats['avg_hook_length']:.1f} chars")
            print(f"  - Avg word count: {stats['avg_word_count']:.1f} words")
        
        print_success(f"Training dataset saved to {output}")
        
    except Exception as e:
        print_error(f"Analysis failed: {e}")
        logger.exception("Analysis error")


@cli.command()
@click.argument('usernames', nargs=-1)
def reset(usernames):
    """Reset profile status to pending"""
    manager = ProfileManager()
    
    if not usernames:
        # Reset all error profiles
        profiles = manager.list_profiles()
        usernames = [p['username'] for p in profiles if p['status'] == 'error']
        
        if not usernames:
            print_info("No profiles with errors to reset")
            return
    
    for username in usernames:
        manager.reset_profile(username)
        print_success(f"Reset profile: @{username.strip().lstrip('@')}")


@cli.command()
@click.option('--force', is_flag=True, help='Force cleanup without confirmation')
def clean(force):
    """Clean up scraped data and reset all profiles"""
    if not force:
        confirm = click.confirm('This will delete all scraped data. Continue?')
        if not confirm:
            print_info("Cleanup cancelled")
            return
    
    # Clean scraped data
    data_dir = Path("scraped_data")
    if data_dir.exists():
        import shutil
        shutil.rmtree(data_dir)
        print_success("Removed scraped data directory")
    
    # Reset profiles
    manager = ProfileManager()
    profiles = manager.list_profiles()
    for profile in profiles:
        manager.reset_profile(profile['username'])
    
    print_success(f"Reset {len(profiles)} profiles")


@cli.command()
def setup():
    """Setup and verify environment"""
    print(f"\n{Fore.CYAN}🔧 Checking environment...{Style.RESET_ALL}")
    
    # Check Python version
    import sys
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"Python version: {python_version}")
    
    # Check required packages
    required_packages = [
        'playwright',
        'beautifulsoup4',
        'loguru',
        'click',
        'fake_useragent',
        'tenacity',
        'pandas',
        'colorama'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print_success(f"{package} installed")
        except ImportError:
            print_error(f"{package} not installed")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n{Fore.YELLOW}Install missing packages with:{Style.RESET_ALL}")
        print(f"pip install {' '.join(missing_packages)}")
    
    # Check Playwright browsers
    print(f"\n{Fore.CYAN}Checking Playwright browsers...{Style.RESET_ALL}")
    try:
        import subprocess
        result = subprocess.run(['playwright', 'install', 'chromium'], capture_output=True, text=True)
        if result.returncode == 0:
            print_success("Playwright Chromium browser installed")
        else:
            print_info("Run: playwright install chromium")
    except Exception as e:
        print_error(f"Playwright browser check failed: {e}")
        print_info("Run: playwright install chromium")
    
    # Check directories
    print(f"\n{Fore.CYAN}Checking directories...{Style.RESET_ALL}")
    dirs = ['scraped_data', 'logs']
    for dir_name in dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir()
            print_success(f"Created {dir_name} directory")
        else:
            print_info(f"{dir_name} directory exists")
    
    print(f"\n{Fore.GREEN}✨ Setup complete!{Style.RESET_ALL}")


if __name__ == '__main__':
    cli()