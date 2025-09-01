#!/usr/bin/env python3
"""
Test script to verify only social-media-optimized originals URLs are being scraped
"""

from enhanced_scraper import EnhancedPinterestScraper

def test_social_media_filter():
    """Test that only social media compatible originals URLs are captured"""
    scraper = EnhancedPinterestScraper(headless=True)
    
    try:
        print("🧪 Testing social media optimized filtering...")
        print("This test checks for: originals URLs + TikTok/Instagram dimensions")
        
        # Test with a single category
        result = scraper.scrape_category("Aesthetic Books", target_count=5, max_scrolls=10)
        
        print(f"\n📊 Results for test scraping:")
        print(f"Total social media ready images found: {len(result['images'])}")
        
        # Verify all URLs are originals AND have dimension data
        originals_count = 0
        has_dimensions_count = 0
        social_media_ready = 0
        
        for img in result['images']:
            url = img['image_url']
            
            # Check if URL is originals
            if 'originals' in url:
                originals_count += 1
            else:
                print(f"❌ Non-original found: {url}")
            
            # Check if has dimension data
            if 'dimensions' in img:
                has_dimensions_count += 1
                dims = img['dimensions']
                width = dims.get('width')
                height = dims.get('height') 
                aspect = dims.get('aspect_ratio')
                score = dims.get('quality_score', 0)
                tier = dims.get('quality_tier', 'unknown')
                
                # Updated to include new croppable ratios
                if aspect in ['9:16', '1:1', '4:5', '3:4', '2:3', '5:8']:
                    social_media_ready += 1
                    tier_emoji = "🔥" if tier == "perfect" else "✂️"
                    print(f"✅ Social media ready: {width}x{height} ({aspect}) - Score: {score} [{tier_emoji} {tier}]")
                else:
                    print(f"❌ Not social media format: {width}x{height} ({aspect})")
            else:
                print(f"❌ Missing dimension data: {url}")
        
        print(f"\n📊 Summary:")
        print(f"✅ Originals URLs: {originals_count}/{len(result['images'])}")
        print(f"📏 Has dimension data: {has_dimensions_count}/{len(result['images'])}")
        print(f"📱 Social media ready: {social_media_ready}/{len(result['images'])}")
        
        success = (originals_count == len(result['images']) and 
                  has_dimensions_count == len(result['images']) and
                  social_media_ready == len(result['images']))
        
        if success and len(result['images']) > 0:
            print("🎉 SUCCESS: All images are social media optimized originals!")
        elif len(result['images']) == 0:
            print("⚠️  No images found - this might be normal, try different category or more scrolls")
        else:
            print("⚠️ ISSUE: Some images don't meet social media criteria")
            
        # Show sample URLs with dimensions
        if result['images']:
            print(f"\n📋 Sample Social Media Ready Images:")
            for i, img in enumerate(result['images'][:3], 1):
                dims = img.get('dimensions', {})
                width = dims.get('width', 'Unknown')
                height = dims.get('height', 'Unknown') 
                aspect = dims.get('aspect_ratio', 'Unknown')
                score = dims.get('quality_score', 0)
                print(f"{i}. {img['image_url']}")
                print(f"   Dimensions: {width}x{height} ({aspect}) Score: {score}")
                
                if aspect == '9:16':
                    print(f"   📱 Perfect for: TikTok, Instagram Stories/Reels")
                elif aspect == '1:1':
                    print(f"   📱 Perfect for: Instagram Posts (Square)")
                elif aspect == '4:5':
                    print(f"   📱 Perfect for: Instagram Feed Posts")
                elif aspect == '3:4':
                    print(f"   📱 Good for: Instagram Reels (slight crop to 9:16)")
                elif aspect == '2:3':
                    print(f"   📱 Good for: Instagram Stories (crop to 9:16)")
                elif aspect == '5:8':
                    print(f"   📱 Good for: TikTok (slight crop to 9:16)")
                print()
            
    finally:
        scraper.close()

if __name__ == "__main__":
    test_social_media_filter()