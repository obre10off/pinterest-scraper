"""
Quick HTML Extractor for TikTok
Optimized for speed - extracts only essential data.
"""

from selenium.webdriver.common.by import By
from typing import List, Dict
import re
from loguru import logger


class QuickExtractor:
    def __init__(self, driver):
        self.driver = driver
        
    def extract_posts_quick(self) -> List[Dict]:
        """Quickly extract essential post data from HTML"""
        posts = []
        
        try:
            # Get all post links at once
            post_links = self.driver.find_elements(By.CSS_SELECTOR, '[data-e2e="user-post-item"] a')
            logger.info(f"Found {len(post_links)} post links")
            
            for idx, link_elem in enumerate(post_links):
                try:
                    href = link_elem.get_attribute('href')
                    if not href:
                        continue
                    
                    post_data = {
                        "index": idx,
                        "id": None,
                        "type": "video",
                        "is_slideshow": False,
                        "caption": "",
                        "hook": "",
                        "url": href
                    }
                    
                    # Detect slideshows from URL
                    if '/photo/' in href:
                        post_data["is_slideshow"] = True
                        post_data["type"] = "slideshow"
                    
                    # Extract ID
                    match = re.search(r'/(video|photo)/(\d+)', href)
                    if match:
                        post_data["id"] = match.group(2)
                    
                    # Try to get any visible text (caption/hook) - quick attempt only
                    try:
                        parent = link_elem.find_element(By.XPATH, '..')
                        text_elements = parent.find_elements(By.TAG_NAME, 'span')
                        for text_elem in text_elements[:3]:  # Check only first 3 spans
                            text = text_elem.text.strip()
                            if text and len(text) > 10:
                                post_data["caption"] = text
                                post_data["hook"] = text[:50].strip() + ("..." if len(text) > 50 else "")
                                break
                    except:
                        pass
                    
                    posts.append(post_data)
                    
                    # Log progress every 20 posts
                    if (idx + 1) % 20 == 0:
                        logger.info(f"Extracted {idx + 1} posts...")
                        
                except Exception as e:
                    logger.debug(f"Error extracting post {idx}: {e}")
                    continue
            
            # Count slideshows
            slideshow_count = sum(1 for p in posts if p["is_slideshow"])
            logger.success(f"Extracted {len(posts)} posts ({slideshow_count} slideshows)")
            
        except Exception as e:
            logger.error(f"Error in quick extraction: {e}")
        
        return posts