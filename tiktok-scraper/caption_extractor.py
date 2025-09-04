#!/usr/bin/env python3
"""
Caption Extractor for TikTok Posts
Extracts captions/hooks by visiting individual post URLs.
"""

import json
import time
import random
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from loguru import logger


class CaptionExtractor:
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.driver = None
        
    def setup_driver(self):
        """Setup Chrome driver"""
        options = Options()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        self.driver = webdriver.Chrome(options=options)
        logger.info("Driver setup completed")
    
    def extract_caption_from_url(self, url: str) -> Dict[str, str]:
        """Extract caption from a single TikTok post URL"""
        result = {"caption": "", "hook": ""}
        
        try:
            self.driver.get(url)
            time.sleep(2)  # Wait for page to load
            
            # Try multiple selectors for caption
            caption_selectors = [
                '[data-e2e="browse-video-desc"]',
                '[data-e2e="video-desc"]',
                '[class*="description"]',
                '[class*="caption"]',
                'h1',
                'span[class*="text"]'
            ]
            
            for selector in caption_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        text = elem.text.strip()
                        if text and len(text) > 10:
                            result["caption"] = text
                            result["hook"] = text[:50].strip() + ("..." if len(text) > 50 else "")
                            logger.debug(f"Found caption: {result['hook']}")
                            return result
                except:
                    continue
                    
        except Exception as e:
            logger.error(f"Error extracting caption from {url}: {e}")
        
        return result
    
    def enrich_posts_with_captions(self, posts: List[Dict], sample_size: int = 10) -> List[Dict]:
        """Enrich posts with captions by visiting URLs"""
        logger.info(f"Enriching {min(sample_size, len(posts))} posts with captions...")
        
        self.setup_driver()
        
        try:
            # Sample posts to avoid taking too long
            sample_posts = posts[:sample_size] if len(posts) > sample_size else posts
            
            for i, post in enumerate(sample_posts):
                if post.get("url"):
                    logger.info(f"Extracting caption {i+1}/{len(sample_posts)}")
                    caption_data = self.extract_caption_from_url(post["url"])
                    post["caption"] = caption_data["caption"]
                    post["hook"] = caption_data["hook"]
                    
                    # Random delay between requests
                    time.sleep(random.uniform(2, 4))
            
            logger.success(f"Enriched {len(sample_posts)} posts with captions")
            
        finally:
            if self.driver:
                self.driver.quit()
        
        return posts


def main():
    """Test caption extraction"""
    # Load existing slideshows
    with open('scraped_data/miiaaa.xox/slideshows.json', 'r') as f:
        posts = json.load(f)
    
    # Enrich with captions (just first 5 for testing)
    extractor = CaptionExtractor(headless=False)
    enriched_posts = extractor.enrich_posts_with_captions(posts, sample_size=5)
    
    # Save enriched data
    with open('scraped_data/miiaaa.xox/slideshows_enriched.json', 'w') as f:
        json.dump(enriched_posts, f, indent=2)
    
    # Show results
    for post in enriched_posts[:5]:
        if post.get("hook"):
            print(f"Hook: {post['hook']}")


if __name__ == "__main__":
    main()