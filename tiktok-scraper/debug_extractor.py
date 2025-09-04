#!/usr/bin/env python3
"""
Debug script to test data extraction from TikTok profile
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import json
import time
from data_extractor import DataExtractor


def debug_tiktok_profile():
    """Debug TikTok profile data extraction"""
    
    # Setup Chrome
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    
    try:
        # Navigate to profile
        username = "miiaaa.xox"
        url = f"https://www.tiktok.com/@{username}"
        print(f"Navigating to: {url}")
        
        driver.get(url)
        time.sleep(5)  # Wait for page to load
        
        print(f"Current URL: {driver.current_url}")
        print(f"Page title: {driver.title}")
        
        # Check for posts
        posts = driver.find_elements(By.CSS_SELECTOR, '[data-e2e="user-post-item"]')
        print(f"Found {len(posts)} post elements")
        
        # Try to find video elements
        videos = driver.find_elements(By.TAG_NAME, 'video')
        print(f"Found {len(videos)} video elements")
        
        # Try different selectors for posts
        alt_selectors = [
            'a[href*="/video/"]',
            '[data-e2e*="post"]',
            '[data-e2e*="video"]',
            'div[class*="video"]',
            'div[class*="item"]'
        ]
        
        for selector in alt_selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            print(f"Selector '{selector}': {len(elements)} elements")
        
        # Check page source for data
        page_source = driver.page_source
        print(f"Page source length: {len(page_source)} characters")
        
        # Check for JSON data
        if '__UNIVERSAL_DATA_FOR_REHYDRATION__' in page_source:
            print("✓ Found __UNIVERSAL_DATA_FOR_REHYDRATION__")
        else:
            print("✗ No __UNIVERSAL_DATA_FOR_REHYDRATION__ found")
        
        if 'SIGI_STATE' in page_source:
            print("✓ Found SIGI_STATE")
        else:
            print("✗ No SIGI_STATE found")
        
        # Try data extraction
        extractor = DataExtractor()
        universal_data = extractor.extract_universal_data(page_source)
        
        if universal_data:
            print(f"✓ Extracted universal data with {len(universal_data)} keys")
            print(f"Keys: {list(universal_data.keys())}")
            
            # Try to extract posts
            posts_data = extractor.extract_profile_posts(universal_data)
            print(f"Extracted {len(posts_data)} posts from data")
        else:
            print("✗ Failed to extract universal data")
        
        # Try JavaScript extraction
        try:
            js_data = driver.execute_script("""
                // Try multiple data sources
                if (document.getElementById('__UNIVERSAL_DATA_FOR_REHYDRATION__')) {
                    return 'UNIVERSAL_DATA found';
                }
                if (window.SIGI_STATE) {
                    return 'SIGI_STATE found';
                }
                if (window.__INIT_DATA__) {
                    return '__INIT_DATA__ found';
                }
                return 'No data found';
            """)
            print(f"JavaScript extraction result: {js_data}")
        except Exception as e:
            print(f"JavaScript extraction failed: {e}")
        
        # Save page source for inspection
        with open('debug_page_source.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        print("Saved page source to debug_page_source.html")
        
    finally:
        driver.quit()


if __name__ == "__main__":
    debug_tiktok_profile()