#!/usr/bin/env python3
"""
Inspect TikTok JSON data structure to understand the format
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import time
from data_extractor import DataExtractor


def inspect_tiktok_data():
    """Inspect TikTok data structure"""
    
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
        
        # Extract data
        extractor = DataExtractor()
        page_source = driver.page_source
        universal_data = extractor.extract_universal_data(page_source)
        
        if universal_data and '__DEFAULT_SCOPE__' in universal_data:
            scope = universal_data['__DEFAULT_SCOPE__']
            
            print("=== DEFAULT_SCOPE structure ===")
            print(f"Keys in __DEFAULT_SCOPE__: {list(scope.keys())}")
            
            # Look for different app sections
            for key in scope.keys():
                if 'webapp' in key:
                    print(f"\n=== {key} ===")
                    webapp_data = scope[key]
                    if isinstance(webapp_data, dict):
                        print(f"Keys: {list(webapp_data.keys())}")
                        
                        # Look for items, posts, or similar
                        for subkey in webapp_data.keys():
                            if any(term in subkey.lower() for term in ['item', 'post', 'video', 'list']):
                                print(f"  → {subkey}: {type(webapp_data[subkey])}")
                                if isinstance(webapp_data[subkey], list):
                                    print(f"    List length: {len(webapp_data[subkey])}")
                                    if webapp_data[subkey]:
                                        sample = webapp_data[subkey][0]
                                        if isinstance(sample, dict):
                                            print(f"    Sample item keys: {list(sample.keys())}")
                                elif isinstance(webapp_data[subkey], dict):
                                    print(f"    Dict keys: {list(webapp_data[subkey].keys())}")
            
            # Check other possible locations
            if 'ItemModule' in universal_data:
                print(f"\n=== ItemModule ===")
                item_module = universal_data['ItemModule']
                print(f"ItemModule type: {type(item_module)}")
                if isinstance(item_module, dict):
                    print(f"ItemModule keys: {list(item_module.keys())[:10]}...")  # First 10 keys
                    
            # Look for any keys containing 'item' or 'video'
            print(f"\n=== Searching for item/video keys ===")
            def search_keys(data, path=""):
                if isinstance(data, dict):
                    for key, value in data.items():
                        current_path = f"{path}.{key}" if path else key
                        if any(term in key.lower() for term in ['item', 'video', 'post']):
                            print(f"Found: {current_path} -> {type(value)}")
                            if isinstance(value, list) and value:
                                print(f"  List length: {len(value)}")
                            elif isinstance(value, dict) and value:
                                print(f"  Dict keys: {list(value.keys())[:5]}...")
                        
                        # Recurse but limit depth
                        if path.count('.') < 3:
                            search_keys(value, current_path)
            
            search_keys(universal_data)
            
            # Save sample data for inspection
            with open('tiktok_data_sample.json', 'w', encoding='utf-8') as f:
                # Just save the structure, not all the data
                sample = {
                    '__DEFAULT_SCOPE__': {
                        key: f"<{type(value).__name__}>" if not isinstance(value, (str, int, bool)) else value
                        for key, value in scope.items()
                    }
                }
                json.dump(sample, f, indent=2)
            print("\nSaved data structure sample to tiktok_data_sample.json")
            
        else:
            print("No universal data found")
        
    finally:
        driver.quit()


if __name__ == "__main__":
    inspect_tiktok_data()