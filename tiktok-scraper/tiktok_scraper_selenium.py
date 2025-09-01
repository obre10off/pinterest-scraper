"""
TikTok Scraper using Selenium (Fallback)
Alternative implementation using Selenium WebDriver when Playwright has issues.
"""

import json
import random
import time
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from loguru import logger
from fake_useragent import UserAgent

from data_extractor import DataExtractor
from html_extractor import HTMLExtractor
from quick_extractor import QuickExtractor
from profile_manager import ProfileManager


class TikTokScraperSelenium:
    def __init__(self, config_path: str = "config.json", headless: bool = False):
        self.config = self.load_config(config_path)
        self.headless = headless or self.config["scraper_settings"]["headless"]
        self.data_extractor = DataExtractor()
        self.profile_manager = ProfileManager(config_path)
        self.ua = UserAgent()
        self.driver = None
        
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
    
    def setup_driver(self):
        """Initialize Chrome WebDriver with anti-detection measures"""
        try:
            logger.info("Setting up Chrome WebDriver...")
            
            # Chrome options
            options = Options()
            
            # Basic options
            if self.headless:
                options.add_argument('--headless')
            
            # Anti-detection arguments
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Window size
            options.add_argument('--window-size=1920,1080')
            
            # User agent
            try:
                user_agent = self.ua.random if self.config["scraper_settings"]["user_agent_rotation"] else self.ua.chrome
                options.add_argument(f'--user-agent={user_agent}')
            except Exception as e:
                logger.warning(f"Error setting user agent: {e}")
            
            # Create driver
            self.driver = webdriver.Chrome(options=options)
            
            # Apply stealth scripts
            if self.config["scraper_settings"]["anti_detection"]:
                self.apply_stealth_scripts()
            
            # Set timeouts
            timeout_seconds = self.config["scraper_settings"]["timeout"] / 1000
            self.driver.implicitly_wait(10)
            self.driver.set_page_load_timeout(timeout_seconds)
            
            logger.success("Chrome WebDriver setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up driver: {e}")
            raise
    
    def apply_stealth_scripts(self):
        """Apply JavaScript to hide automation"""
        try:
            stealth_script = """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            """
            self.driver.execute_script(stealth_script)
        except Exception as e:
            logger.warning(f"Error applying stealth scripts: {e}")
    
    def random_delay(self, min_seconds: Optional[float] = None, max_seconds: Optional[float] = None):
        """Add random delay for rate limiting"""
        min_delay = min_seconds or self.config["rate_limiting"]["min_delay"]
        max_delay = max_seconds or self.config["rate_limiting"]["max_delay"]
        delay = random.uniform(min_delay, max_delay)
        logger.debug(f"Waiting {delay:.2f} seconds...")
        time.sleep(delay)
    
    def navigate_to_profile(self, username: str) -> bool:
        """Navigate to TikTok profile page"""
        try:
            # Clean username
            username = username.strip().lstrip('@')
            url = f"https://www.tiktok.com/@{username}"
            
            logger.info(f"Navigating to profile: @{username}")
            
            # Navigate to profile
            self.driver.get(url)
            
            # Wait for page to load
            wait = WebDriverWait(self.driver, 15)
            
            # Try to find profile content
            try:
                # Wait for profile posts or profile info
                wait.until(
                    lambda d: d.find_element(By.CSS_SELECTOR, '[data-e2e="user-post-item"]') or
                              d.find_element(By.CSS_SELECTOR, '[data-e2e="profile-header"]') or
                              d.find_element(By.TAG_NAME, 'video')
                )
                logger.success(f"Successfully loaded profile: @{username}")
                return True
            except TimeoutException:
                # Try alternative selectors
                if self.driver.find_elements(By.TAG_NAME, 'video') or \
                   "tiktok.com" in self.driver.current_url:
                    logger.success(f"Profile loaded (alternative detection): @{username}")
                    return True
                else:
                    logger.error(f"Profile content not found for @{username}")
                    return False
            
        except Exception as e:
            logger.error(f"Error navigating to profile @{username}: {e}")
            return False
    
    def scroll_and_load_posts(self) -> int:
        """Scroll page to load more posts"""
        posts_loaded = 0
        max_scrolls = self.config["scraper_settings"]["max_scrolls"]
        scroll_pause = self.config["scraper_settings"]["scroll_pause_time"]
        
        logger.info("Starting to scroll and load posts...")
        
        for scroll_count in range(max_scrolls):
            # Get current post count
            posts = self.driver.find_elements(By.CSS_SELECTOR, '[data-e2e="user-post-item"]')
            current_count = len(posts)
            
            # Scroll down
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Wait for new content
            time.sleep(scroll_pause + random.uniform(0, 2))
            
            # Check if new posts loaded
            new_posts = self.driver.find_elements(By.CSS_SELECTOR, '[data-e2e="user-post-item"]')
            new_count = len(new_posts)
            
            if new_count == current_count:
                logger.info(f"No new posts loaded after scroll {scroll_count + 1}")
                break
            
            posts_loaded = new_count
            logger.info(f"Loaded {posts_loaded} posts after scroll {scroll_count + 1}")
            
            # Longer pause every few scrolls
            if (scroll_count + 1) % 5 == 0:
                logger.info("Taking extended break...")
                self.random_delay(5, 10)
        
        return posts_loaded
    
    def extract_page_data(self) -> Optional[Dict]:
        """Extract data from current page"""
        try:
            # Get page source
            html_content = self.driver.page_source
            
            # Extract universal data using the data extractor
            universal_data = self.data_extractor.extract_universal_data(html_content)
            
            if not universal_data:
                logger.warning("No universal data found, trying JavaScript extraction...")
                
                # Try to extract data directly via JavaScript
                try:
                    universal_data = self.driver.execute_script("""
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
                        
                        return null;
                    """)
                except Exception as e:
                    logger.warning(f"JavaScript extraction failed: {e}")
            
            return universal_data
            
        except Exception as e:
            logger.error(f"Error extracting page data: {e}")
            return None
    
    def extract_posts_fallback(self) -> List[Dict]:
        """Fallback to HTML extraction when JSON is empty"""
        logger.info("Using quick HTML extraction as fallback...")
        quick_extractor = QuickExtractor(self.driver)
        return quick_extractor.extract_posts_quick()
    
    def scrape_profile(self, username: str) -> Dict:
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
            if not self.navigate_to_profile(username):
                raise Exception("Failed to navigate to profile")
            
            # Random delay after navigation
            self.random_delay(2, 5)
            
            # Scroll to load posts
            posts_loaded = self.scroll_and_load_posts()
            logger.info(f"Total posts loaded: {posts_loaded}")
            
            # Extract data from page
            page_data = self.extract_page_data()
            
            # Try JSON extraction first
            all_posts = []
            if page_data:
                all_posts = self.data_extractor.extract_profile_posts(page_data)
                
            # If no posts from JSON, try HTML extraction
            if not all_posts:
                logger.warning("No posts from JSON, trying HTML extraction...")
                all_posts = self.extract_posts_fallback()
            
            result["total_posts"] = len(all_posts)
            
            if all_posts:
                # Filter for slideshows if configured
                if self.config["scraper_settings"]["slideshows_only"]:
                    # Filter for slideshow posts
                    filtered_posts = [
                        post for post in all_posts 
                        if post and post.get("is_slideshow")
                    ]
                    result["posts"] = filtered_posts
                    result["slideshow_posts"] = len(filtered_posts)
                else:
                    # Use all posts
                    result["posts"] = all_posts
                    # Count slideshows
                    result["slideshow_posts"] = sum(
                        1 for post in all_posts 
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
                logger.warning(f"No posts extracted for @{username}")
            
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
    
    def scrape_multiple_profiles(self, usernames: List[str]) -> List[Dict]:
        """Scrape multiple TikTok profiles"""
        results = []
        
        if not usernames:
            logger.warning("No usernames provided")
            return results
        
        try:
            # Setup driver once
            logger.info("Setting up Chrome WebDriver for scraping...")
            self.setup_driver()
            
            for i, username in enumerate(usernames):
                logger.info(f"Scraping profile {i+1}/{len(usernames)}: @{username}")
                
                try:
                    # Scrape profile
                    result = self.scrape_profile(username)
                    results.append(result)
                    
                    # Save result immediately
                    if result and not result.get("error"):
                        self.save_profile_data(result)
                    
                    # Delay between profiles
                    if i < len(usernames) - 1:
                        logger.info("Taking break between profiles...")
                        self.random_delay(10, 20)
                        
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
            self.cleanup()
        
        return results
    
    def save_profile_data(self, data: Dict):
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
    
    def cleanup(self):
        """Clean up driver resources"""
        try:
            if self.driver:
                logger.info("Closing Chrome WebDriver...")
                self.driver.quit()
                self.driver = None
                logger.success("Driver cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


def main():
    """Main function for testing"""
    scraper = TikTokScraperSelenium(headless=False)
    
    # Test with sample profiles
    test_profiles = ["miiaaa.xox"]
    
    results = scraper.scrape_multiple_profiles(test_profiles)
    
    # Print summary
    for result in results:
        print(f"\n@{result['username']}:")
        print(f"  Total posts: {result['total_posts']}")
        print(f"  Slideshow posts: {result['slideshow_posts']}")
        print(f"  Hooks extracted: {len(result['hooks'])}")
        if result.get("error"):
            print(f"  Error: {result['error']}")


if __name__ == "__main__":
    main()