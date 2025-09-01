#!/usr/bin/env python3
"""
Debug test to see what's being found and filtered
"""

from enhanced_scraper import EnhancedPinterestScraper
from selenium.webdriver.common.by import By
import time

def debug_test():
    scraper = EnhancedPinterestScraper(headless=False)
    
    try:
        print("🧪 Debug Test - Finding out what's being filtered")
        print("=" * 60)
        
        category = "wallpaper aesthetic"
        url = f"https://www.pinterest.com/search/pins/?q={category}"
        scraper.driver.get(url)
        time.sleep(3)
        
        # Find ALL images on page
        all_imgs = scraper.driver.find_elements(By.CSS_SELECTOR, "img[src*='pinimg.com']")
        print(f"\n📊 Found {len(all_imgs)} total images on page")
        
        # Analyze a sample
        print("\n🔍 Analyzing first 20 images:")
        print("-" * 60)
        
        originals_count = 0
        video_count = 0
        convertible_count = 0
        
        for i, img in enumerate(all_imgs[:20], 1):
            try:
                src = img.get_attribute('src')
                if not src:
                    continue
                    
                print(f"\n{i}. Source URL analysis:")
                print(f"   Raw: {src[:100]}...")
                
                # Check what type it is
                if 'originals' in src:
                    if '/videos/' in src or '.0000000.' in src:
                        print("   ❌ Type: Video thumbnail (has originals but is video)")
                        video_count += 1
                    else:
                        print("   ✅ Type: Already original image")
                        originals_count += 1
                elif any(size in src for size in ['/236x/', '/474x/', '/736x/', '/564x/']):
                    print("   🔄 Type: Convertible thumbnail")
                    converted = scraper.convert_to_original_url(src)
                    if converted:
                        print(f"   ✅ Converted to: {converted[:80]}...")
                        convertible_count += 1
                    else:
                        print("   ❌ Could not convert (might be video)")
                elif '/60x60/' in src or '/75x75/' in src:
                    print("   ❌ Type: Profile picture (too small)")
                else:
                    print(f"   ❓ Type: Unknown pattern")
                    
            except Exception as e:
                print(f"   Error: {e}")
        
        print("\n" + "=" * 60)
        print("📊 Summary of first 20 images:")
        print(f"  • Already originals (non-video): {originals_count}")
        print(f"  • Convertible thumbnails: {convertible_count}")
        print(f"  • Video thumbnails: {video_count}")
        print(f"  • Potentially usable: {originals_count + convertible_count}")
        
        # Now test actual scraping
        print("\n" + "=" * 60)
        print("🚀 Testing actual scraping with 5 images...")
        result = scraper.scrape_category(category, target_count=5, max_scrolls=10)
        
        print(f"\n✅ Successfully scraped: {len(result['images'])} images")
        if result['images']:
            print("\n📱 Images found:")
            for img in result['images']:
                dims = img.get('dimensions', {})
                url = img['image_url']
                print(f"  • {dims.get('width')}x{dims.get('height')} - {url[:80]}...")
                
    finally:
        scraper.close()

if __name__ == "__main__":
    debug_test()