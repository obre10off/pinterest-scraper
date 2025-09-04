#!/usr/bin/env python3
"""
Final test with all fixes applied
"""

from enhanced_scraper import EnhancedPinterestScraper

def final_test():
    # Test with 3 diverse categories
    test_categories = [
        "Aesthetic wallpaper",  # Usually has many 9:16 images
        "Instagram posts",      # Should have 1:1 images
        "Phone backgrounds"     # Should have 9:16 images
    ]
    
    scraper = EnhancedPinterestScraper(headless=False)
    
    try:
        total_found = 0
        results_summary = {}
        
        for category in test_categories:
            print(f"\n{'='*60}")
            print(f"Testing: {category}")
            print('='*60)
            
            result = scraper.scrape_category(category, target_count=15, max_scrolls=30)
            
            found = len(result['images'])
            total_found += found
            results_summary[category] = found
            
            print(f"\n✅ Found {found} images for {category}")
            
            if result['images']:
                # Analyze what we found
                aspect_ratios = {}
                for img in result['images']:
                    dims = img.get('dimensions', {})
                    ratio = dims.get('aspect_ratio', 'unknown')
                    aspect_ratios[ratio] = aspect_ratios.get(ratio, 0) + 1
                
                print("📊 Aspect ratio breakdown:")
                for ratio, count in aspect_ratios.items():
                    print(f"   • {ratio}: {count} images")
                
                # Show first 3 URLs to verify they're not videos
                print("\n🔗 Sample URLs (first 3):")
                for i, img in enumerate(result['images'][:3], 1):
                    url = img['image_url']
                    # Check it's not a video
                    if '/videos/' not in url and '.0000000.' not in url:
                        print(f"   {i}. ✅ {url[:80]}...")
                    else:
                        print(f"   {i}. ❌ VIDEO: {url[:80]}...")
        
        print(f"\n{'='*60}")
        print("📊 FINAL SUMMARY")
        print('='*60)
        for category, count in results_summary.items():
            status = "✅" if count > 0 else "❌"
            print(f"{status} {category}: {count} images")
        
        print(f"\n🎯 Total images found: {total_found}")
        
        if total_found < 15:
            print("\n⚠️  Still finding too few images. Issues may include:")
            print("   • Pinterest might be blocking or rate limiting")
            print("   • Categories might not have many compatible images")
            print("   • Need to try different search terms")
        elif total_found < 30:
            print("\n⚠️  Moderate yield. Could be improved by:")
            print("   • Using more popular search terms")
            print("   • Increasing scroll attempts")
            print("   • Adjusting tolerance further")
        else:
            print("\n✅ Good yield! The scraper is working well.")
            
    finally:
        scraper.close()

if __name__ == "__main__":
    final_test()