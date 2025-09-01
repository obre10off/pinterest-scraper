"""
HTML Data Extractor for TikTok
Extracts post data directly from HTML elements when JSON is unavailable.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from typing import List, Dict, Optional
import re
from loguru import logger


class HTMLExtractor:
    def __init__(self, driver):
        self.driver = driver
        
    def extract_posts_from_html(self) -> List[Dict]:
        """Extract post data directly from HTML elements"""
        posts = []
        
        try:
            # Find all post elements
            post_elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-e2e="user-post-item"]')
            logger.info(f"Found {len(post_elements)} post elements in HTML")
            
            for idx, post_elem in enumerate(post_elements):
                try:
                    post_data = self.extract_single_post(post_elem, idx)
                    if post_data:
                        posts.append(post_data)
                except Exception as e:
                    logger.warning(f"Error extracting post {idx}: {e}")
                    continue
            
            logger.success(f"Extracted {len(posts)} posts from HTML")
            
        except Exception as e:
            logger.error(f"Error extracting posts from HTML: {e}")
        
        return posts
    
    def extract_single_post(self, post_elem: WebElement, index: int) -> Optional[Dict]:
        """Extract data from a single post element (optimized)"""
        try:
            post_data = {
                "index": index,
                "id": None,
                "type": "unknown",
                "is_slideshow": False,
                "caption": "",
                "hook": "",
                "url": None,
                "stats": {},
                "media": {}
            }
            
            # Quick check for post URL - this is the most important
            try:
                # Get the first link which is usually the post link
                link = post_elem.find_element(By.TAG_NAME, 'a')
                href = link.get_attribute('href')
                if href:
                    post_data["url"] = href
                    # Quick slideshow detection from URL
                    if '/photo/' in href:
                        post_data["is_slideshow"] = True
                        post_data["type"] = "slideshow"
                    else:
                        post_data["type"] = "video"
                    
                    # Extract ID from URL
                    match = re.search(r'/(video|photo)/(\d+)', href)
                    if match:
                        post_data["id"] = match.group(2)
            except:
                pass
            
            # Check for slideshow indicators
            try:
                # Look for multiple image indicators
                carousel_indicators = post_elem.find_elements(By.CSS_SELECTOR, '[class*="carousel"], [class*="slide"], [class*="photo"]')
                if carousel_indicators:
                    post_data["is_slideshow"] = True
                    post_data["type"] = "slideshow"
                
                # Check for image icon or slideshow icon
                svg_elements = post_elem.find_elements(By.TAG_NAME, 'svg')
                for svg in svg_elements:
                    if 'image' in svg.get_attribute('class', '').lower() or \
                       'photo' in svg.get_attribute('class', '').lower():
                        post_data["is_slideshow"] = True
                        post_data["type"] = "slideshow"
                        break
            except:
                pass
            
            # Extract caption/text
            try:
                # Look for description or caption elements
                text_selectors = [
                    '[data-e2e*="description"]',
                    '[class*="caption"]',
                    '[class*="description"]',
                    '[class*="text"]',
                    'span',
                    'div[class*="content"]'
                ]
                
                for selector in text_selectors:
                    text_elements = post_elem.find_elements(By.CSS_SELECTOR, selector)
                    for text_elem in text_elements:
                        text = text_elem.text.strip()
                        if text and len(text) > len(post_data["caption"]):
                            post_data["caption"] = text
                            # Extract hook (first 50 chars)
                            post_data["hook"] = text[:50].strip() + ("..." if len(text) > 50 else "")
                            break
                    if post_data["caption"]:
                        break
            except:
                pass
            
            # Extract stats (views, likes, etc.)
            try:
                # Look for stat elements
                stat_selectors = [
                    '[class*="stats"]',
                    '[class*="count"]',
                    '[class*="number"]',
                    'strong'
                ]
                
                for selector in stat_selectors:
                    stat_elements = post_elem.find_elements(By.CSS_SELECTOR, selector)
                    for stat_elem in stat_elements:
                        text = stat_elem.text.strip()
                        # Parse numbers like "1.2M", "523K", etc.
                        if text:
                            number = self.parse_stat_number(text)
                            if number > 0:
                                # Try to determine what type of stat
                                parent_text = stat_elem.find_element(By.XPATH, '..').text.lower()
                                if 'like' in parent_text:
                                    post_data["stats"]["likes"] = number
                                elif 'view' in parent_text or 'play' in parent_text:
                                    post_data["stats"]["views"] = number
                                elif 'comment' in parent_text:
                                    post_data["stats"]["comments"] = number
                                elif 'share' in parent_text:
                                    post_data["stats"]["shares"] = number
            except:
                pass
            
            # Extract thumbnail/cover image
            try:
                img_elements = post_elem.find_elements(By.TAG_NAME, 'img')
                for img in img_elements:
                    src = img.get_attribute('src')
                    if src and 'tiktok' in src:
                        post_data["media"]["cover_url"] = src
                        break
            except:
                pass
            
            return post_data
            
        except Exception as e:
            logger.error(f"Error extracting single post: {e}")
            return None
    
    def parse_stat_number(self, text: str) -> int:
        """Parse stat numbers like '1.2M' to actual integers"""
        try:
            text = text.strip().upper()
            if 'M' in text:
                number = float(text.replace('M', '').replace(',', ''))
                return int(number * 1000000)
            elif 'K' in text:
                number = float(text.replace('K', '').replace(',', ''))
                return int(number * 1000)
            else:
                return int(text.replace(',', ''))
        except:
            return 0
    
    def detect_slideshow_posts(self) -> List[WebElement]:
        """Specifically find slideshow/carousel posts"""
        slideshow_posts = []
        
        try:
            # Find all posts
            all_posts = self.driver.find_elements(By.CSS_SELECTOR, '[data-e2e="user-post-item"]')
            
            for post in all_posts:
                is_slideshow = False
                
                # Method 1: Check for photo URL
                try:
                    links = post.find_elements(By.TAG_NAME, 'a')
                    for link in links:
                        href = link.get_attribute('href')
                        if href and '/photo/' in href:
                            is_slideshow = True
                            break
                except:
                    pass
                
                # Method 2: Check for slideshow indicators in classes
                if not is_slideshow:
                    try:
                        html = post.get_attribute('innerHTML')
                        if any(indicator in html.lower() for indicator in ['slideshow', 'carousel', 'photo', 'image']):
                            is_slideshow = True
                    except:
                        pass
                
                # Method 3: Check for multiple image dots/indicators
                if not is_slideshow:
                    try:
                        # Look for pagination dots
                        dots = post.find_elements(By.CSS_SELECTOR, '[class*="dot"], [class*="indicator"]')
                        if len(dots) > 1:
                            is_slideshow = True
                    except:
                        pass
                
                if is_slideshow:
                    slideshow_posts.append(post)
            
            logger.info(f"Found {len(slideshow_posts)} slideshow posts out of {len(all_posts)} total")
            
        except Exception as e:
            logger.error(f"Error detecting slideshow posts: {e}")
        
        return slideshow_posts