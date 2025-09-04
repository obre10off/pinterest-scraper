#!/usr/bin/env python3
"""
Quick test with a single category
"""

from enhanced_scraper import EnhancedPinterestScraper

def test_single_category():
    scraper = EnhancedPinterestScraper(headless=False)  # Use non-headless to see what's happening
    
    try:
        print("🧪 Testing single category scrape with improved settings")
        print("=" * 60)
        
        # Test with a popular category that should have many images
        result = scraper.scrape_category("Aesthetic wallpaper", target_count=10, max_scrolls=20)
        
        print(f"\n📊 Results:")
        print(f"Found {len(result['images'])} social media compatible images")
        
        if result['images']:
            print("\n📱 Sample images found:")
            for i, img in enumerate(result['images'][:5], 1):
                dims = img.get('dimensions', {})
                print(f"{i}. {dims.get('width')}x{dims.get('height')} ({dims.get('aspect_ratio')}) - Score: {dims.get('quality_score')} [{dims.get('quality_tier')}]")
                print(f"   URL: {img['image_url'][:80]}...")
        else:
            print("❌ No compatible images found")
            
    finally:
        scraper.close()

if __name__ == "__main__":
    test_single_category()