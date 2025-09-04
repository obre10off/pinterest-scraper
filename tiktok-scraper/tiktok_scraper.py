"""
Core TikTok Scraper using Playwright
Main scraping engine with anti-detection measures and slideshow filtering.
"""

import asyncio
import json
import random
import time
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime

from playwright.async_api import async_playwright, Page, Browser
from loguru import logger
from fake_useragent import UserAgent
from tenacity import retry, stop_after_attempt, wait_exponential

from data_extractor import DataExtractor
from profile_manager import ProfileManager


class TikTokScraper:
    def __init__(self, config_path: str = "config.json", headless: bool = False):
        self.config = self.load_config(config_path)
        self.headless = headless or self.config["scraper_settings"]["headless"]
        self.data_extractor = DataExtractor()
        self.profile_manager = ProfileManager(config_path)
        self.ua = UserAgent()
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
    def load_config(self, config_path: str) -> dict:
        """Load configuration from file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Config file {config_path} not found")
            return self.get_default_config()
    
    def get_default_config(self) -> dict:
        """Return default configuration"""
        return {
            "scraper_settings": {
                "headless": False,
                "timeout": 30000,
                "scroll_pause_time": 3,
                "max_scrolls": 10,
                "user_agent_rotation": True,
                "anti_detection": True,
                "slideshows_only": True
            },
            "rate_limiting": {
                "min_delay": 3,
                "max_delay": 10
            }
        }
    
    async def setup_browser(self):
        """Initialize browser with simplified configuration"""
        try:
            # Start Playwright
            logger.info("Starting Playwright...")
            self.playwright = await async_playwright().start()
            
            # Simplified browser arguments
            browser_args = [
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ]
            
            # Launch browser with minimal config
            logger.info(f"Launching browser (headless: {self.headless})...")
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=browser_args
            )
            
            # Create simple context
            logger.info("Creating browser context...")
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080}
            )
            
            # Create page
            logger.info("Creating new page...")
            self.page = await self.context.new_page()
            
            # Set reasonable timeouts
            timeout = self.config["scraper_settings"]["timeout"]
            self.page.set_default_timeout(timeout)
            self.page.set_default_navigation_timeout(timeout)
            
            logger.success("Browser setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up browser: {e}")
            await self.cleanup()
            raise
    
    async def apply_stealth_scripts(self):
        """Apply stealth JavaScript to hide automation"""
        stealth_js = """
        () => {
            // Override navigator.webdriver
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Override plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Override languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            
            // Override permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            // Override chrome
            window.chrome = {
                runtime: {},
                app: {
                    isInstalled: false,
                    InstallState: {
                        DISABLED: 'disabled',
                        INSTALLED: 'installed',
                        NOT_INSTALLED: 'not_installed'
                    },
                    RunningState: {
                        CANNOT_RUN: 'cannot_run',
                        READY_TO_RUN: 'ready_to_run',
                        RUNNING: 'running'
                    }
                }
            };
            
            // Remove automation indicators
            const newProto = navigator.__proto__;
            delete newProto.webdriver;
            navigator.__proto__ = newProto;
        }
        """
        
        await self.context.add_init_script(stealth_js)
    
    async def random_delay(self, min_seconds: Optional[float] = None, max_seconds: Optional[float] = None):
        """Add random delay for rate limiting"""
        min_delay = min_seconds or self.config["rate_limiting"]["min_delay"]
        max_delay = max_seconds or self.config["rate_limiting"]["max_delay"]
        delay = random.uniform(min_delay, max_delay)
        logger.debug(f"Waiting {delay:.2f} seconds...")
        await asyncio.sleep(delay)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def navigate_to_profile(self, username: str) -> bool:
        """Navigate to TikTok profile page"""
        try:
            # Clean username
            username = username.strip().lstrip('@')
            url = f"https://www.tiktok.com/@{username}"
            
            logger.info(f"Navigating to profile: @{username}")
            
            # Navigate with timeout
            await self.page.goto(url, wait_until='networkidle', timeout=self.config["scraper_settings"]["timeout"])
            
            # Wait for content to load
            await self.page.wait_for_selector('div[data-e2e="user-post-item"]', timeout=10000)
            
            # Random delay to appear human
            await self.random_delay(2, 5)
            
            logger.success(f"Successfully loaded profile: @{username}")
            return True
            
        except Exception as e:
            logger.error(f"Error navigating to profile @{username}: {e}")
            return False
    
    async def scroll_and_load_posts(self) -> int:
        """Scroll page to load more posts"""
        posts_loaded = 0
        max_scrolls = self.config["scraper_settings"]["max_scrolls"]
        scroll_pause = self.config["scraper_settings"]["scroll_pause_time"]
        
        for scroll_count in range(max_scrolls):
            # Get current post count
            posts = await self.page.query_selector_all('div[data-e2e="user-post-item"]')
            current_count = len(posts)
            
            # Scroll down
            await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            
            # Random human-like pause
            await asyncio.sleep(scroll_pause + random.uniform(0, 2))
            
            # Check if new posts loaded
            new_posts = await self.page.query_selector_all('div[data-e2e="user-post-item"]')
            new_count = len(new_posts)
            
            if new_count == current_count:
                logger.info(f"No new posts loaded after scroll {scroll_count + 1}")
                break
            
            posts_loaded = new_count
            logger.info(f"Loaded {posts_loaded} posts after scroll {scroll_count + 1}")
            
            # Longer pause every few scrolls
            if (scroll_count + 1) % 5 == 0:
                logger.info("Taking extended break...")
                await self.random_delay(5, 10)
        
        return posts_loaded
    
    async def extract_page_data(self) -> Optional[Dict]:
        """Extract data from current page"""
        try:
            # Get page HTML
            html_content = await self.page.content()
            
            # Extract universal data
            universal_data = self.data_extractor.extract_universal_data(html_content)
            
            if not universal_data:
                logger.warning("Failed to extract universal data, trying alternative methods...")
                
                # Try to extract data from page evaluation
                universal_data = await self.page.evaluate("""
                    () => {
                        // Try to get UNIVERSAL_DATA
                        const universalScript = document.getElementById('__UNIVERSAL_DATA_FOR_REHYDRATION__');
                        if (universalScript && universalScript.textContent) {
                            try {
                                return JSON.parse(universalScript.textContent);
                            } catch (e) {
                                console.error('Error parsing universal data:', e);
                            }
                        }
                        
                        // Try SIGI_STATE
                        if (window.SIGI_STATE) {
                            return window.SIGI_STATE;
                        }
                        
                        // Try __INIT_DATA__
                        if (window.__INIT_DATA__) {
                            return window.__INIT_DATA__;
                        }
                        
                        return null;
                    }
                """)
            
            return universal_data
            
        except Exception as e:
            logger.error(f"Error extracting page data: {e}")
            return None
    
    async def scrape_profile(self, username: str) -> Dict:
        """Scrape a single TikTok profile"""
        result = {
            "username": username.strip().lstrip('@'),
            "scraped_at": datetime.now().isoformat(),
            "total_posts": 0,
            "slideshow_posts": 0,
            "posts": [],
            "hooks": [],
            "error": None
        }
        
        try:
            # Update profile status
            self.profile_manager.update_profile_status(username, "in_progress")
            
            # Navigate to profile
            if not await self.navigate_to_profile(username):
                raise Exception("Failed to navigate to profile")
            
            # Scroll to load posts
            posts_loaded = await self.scroll_and_load_posts()
            logger.info(f"Total posts loaded: {posts_loaded}")
            
            # Extract data from page
            page_data = await self.extract_page_data()
            
            if page_data:
                # Extract posts from data
                all_posts = self.data_extractor.extract_profile_posts(page_data)
                result["total_posts"] = len(all_posts)
                
                # Filter for slideshows if configured
                if self.config["scraper_settings"]["slideshows_only"]:
                    filtered_posts = self.data_extractor.filter_slideshow_posts(all_posts)
                    result["posts"] = filtered_posts
                    result["slideshow_posts"] = len(filtered_posts)
                else:
                    # Extract all posts
                    result["posts"] = [
                        self.data_extractor.extract_post_data(post) 
                        for post in all_posts
                    ]
                    # Count slideshows
                    result["slideshow_posts"] = sum(
                        1 for post in result["posts"] 
                        if post and post.get("is_slideshow")
                    )
                
                # Extract hooks
                result["hooks"] = [
                    post["hook"] 
                    for post in result["posts"] 
                    if post and post.get("hook")
                ]
                
                logger.success(f"Scraped @{username}: {result['total_posts']} total, {result['slideshow_posts']} slideshows")
            else:
                logger.warning(f"No data extracted for @{username}")
            
            # Update profile stats
            self.profile_manager.update_profile_stats(
                username, 
                result["total_posts"], 
                result["slideshow_posts"]
            )
            self.profile_manager.update_profile_status(username, "completed")
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error scraping @{username}: {error_msg}")
            result["error"] = error_msg
            self.profile_manager.update_profile_status(username, "error", error_msg)
        
        return result
    
    async def scrape_multiple_profiles(self, usernames: List[str]) -> List[Dict]:
        """Scrape multiple TikTok profiles"""
        results = []
        
        if not usernames:
            logger.warning("No usernames provided")
            return results
        
        try:
            # Setup browser once
            logger.info("Setting up browser for scraping...")
            await self.setup_browser()
            
            # Verify browser is working
            if not self.page:
                raise Exception("Browser page not initialized")
            
            for i, username in enumerate(usernames):
                logger.info(f"Scraping profile {i+1}/{len(usernames)}: @{username}")
                
                try:
                    # Scrape profile
                    result = await self.scrape_profile(username)
                    results.append(result)
                    
                    # Save result immediately
                    if result and not result.get("error"):
                        await self.save_profile_data(result)
                    
                    # Delay between profiles
                    if i < len(usernames) - 1:
                        logger.info("Taking break between profiles...")
                        await self.random_delay(10, 20)
                        
                except Exception as e:
                    logger.error(f"Failed to scrape @{username}: {e}")
                    # Add failed result
                    results.append({
                        "username": username.strip().lstrip('@'),
                        "scraped_at": None,
                        "total_posts": 0,
                        "slideshow_posts": 0,
                        "posts": [],
                        "hooks": [],
                        "error": str(e)
                    })
                    # Continue with next profile
                    continue
            
        except Exception as e:
            logger.error(f"Fatal error during scraping: {e}")
            raise
        finally:
            # Always cleanup
            logger.info("Cleaning up browser resources...")
            await self.cleanup()
        
        return results
    
    async def save_profile_data(self, data: Dict):
        """Save scraped data to files"""
        username = data["username"]
        output_dir = self.profile_manager.get_profile_output_dir(username)
        
        # Save slideshows JSON
        if data["posts"]:
            slideshows_file = output_dir / "slideshows.json"
            with open(slideshows_file, 'w', encoding='utf-8') as f:
                json.dump(data["posts"], f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(data['posts'])} posts to {slideshows_file}")
        
        # Save hooks text file
        if data["hooks"]:
            hooks_file = output_dir / "hooks.txt"
            with open(hooks_file, 'w', encoding='utf-8') as f:
                for hook in data["hooks"]:
                    f.write(hook + "\n\n")
            logger.info(f"Saved {len(data['hooks'])} hooks to {hooks_file}")
        
        # Save metadata
        metadata_file = output_dir / "metadata.json"
        metadata = {
            "username": username,
            "scraped_at": data["scraped_at"],
            "total_posts": data["total_posts"],
            "slideshow_posts": data["slideshow_posts"],
            "hooks_count": len(data["hooks"]),
            "error": data.get("error")
        }
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
    
    async def cleanup(self):
        """Clean up browser resources"""
        try:
            logger.info("Starting cleanup...")
            
            if hasattr(self, 'page') and self.page:
                try:
                    await self.page.close()
                    logger.debug("Page closed")
                except Exception as e:
                    logger.warning(f"Error closing page: {e}")
                    
            if hasattr(self, 'context') and self.context:
                try:
                    await self.context.close()
                    logger.debug("Context closed")
                except Exception as e:
                    logger.warning(f"Error closing context: {e}")
                    
            if hasattr(self, 'browser') and self.browser:
                try:
                    await self.browser.close()
                    logger.debug("Browser closed")
                except Exception as e:
                    logger.warning(f"Error closing browser: {e}")
                    
            if hasattr(self, 'playwright') and self.playwright:
                try:
                    await self.playwright.stop()
                    logger.debug("Playwright stopped")
                except Exception as e:
                    logger.warning(f"Error stopping playwright: {e}")
            
            # Reset references
            self.page = None
            self.context = None
            self.browser = None
            self.playwright = None
            
            logger.success("Browser cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


async def main():
    """Main function for testing"""
    scraper = TikTokScraper()
    
    # Test with sample profiles
    test_profiles = ["@test_user"]  # Replace with actual profiles
    
    results = await scraper.scrape_multiple_profiles(test_profiles)
    
    # Print summary
    for result in results:
        print(f"\n@{result['username']}:")
        print(f"  Total posts: {result['total_posts']}")
        print(f"  Slideshow posts: {result['slideshow_posts']}")
        print(f"  Hooks extracted: {len(result['hooks'])}")
        if result.get("error"):
            print(f"  Error: {result['error']}")


if __name__ == "__main__":
    asyncio.run(main())