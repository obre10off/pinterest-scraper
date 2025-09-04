#!/usr/bin/env python3
"""
Test the URL conversion functionality
"""

from enhanced_scraper import EnhancedPinterestScraper

def test_url_conversion():
    """Test converting thumbnail URLs to originals"""
    scraper = EnhancedPinterestScraper(headless=True)
    
    test_urls = [
        # Common thumbnail sizes
        "https://i.pinimg.com/236x/8a/06/c7/8a06c7cb1f199a52d7dca09f74e46bea.jpg",
        "https://i.pinimg.com/474x/8a/06/c7/8a06c7cb1f199a52d7dca09f74e46bea.jpg",
        "https://i.pinimg.com/736x/8a/06/c7/8a06c7cb1f199a52d7dca09f74e46bea.jpg",
        "https://i.pinimg.com/564x/8a/06/c7/8a06c7cb1f199a52d7dca09f74e46bea.jpg",
        # Already original
        "https://i.pinimg.com/originals/8a/06/c7/8a06c7cb1f199a52d7dca09f74e46bea.jpg",
        # Video thumbnail (should be handled)
        "https://i.pinimg.com/videos/thumbnails/originals/8a/06/c7/8a06c7cb1f199a52d7dca09f74e46bea.0000000.jpg",
    ]
    
    print("🧪 Testing URL Conversion")
    print("=" * 60)
    
    for url in test_urls:
        converted = scraper.convert_to_original_url(url)
        print(f"\n📍 Input:  {url}")
        print(f"✨ Output: {converted}")
        
        if converted and 'originals' in converted and '/videos/' not in converted:
            print("✅ Successfully converted to originals URL")
        elif not converted:
            print("❌ Could not convert URL")
        else:
            print("⚠️ Conversion result may have issues")
    
    scraper.close()
    print("\n✅ URL conversion test complete!")

def test_dimension_check():
    """Test the expanded dimension compatibility"""
    scraper = EnhancedPinterestScraper(headless=True)
    
    print("\n🧪 Testing Expanded Dimension Compatibility")
    print("=" * 60)
    
    test_dimensions = [
        (500, 889),   # 9:16 but low res
        (600, 1067),  # 9:16 minimum acceptable
        (720, 1280),  # 9:16 good quality
        (1080, 1920), # 9:16 perfect
        (500, 500),   # 1:1 low res
        (800, 1000),  # 4:5 good
        (750, 1000),  # 3:4 croppable
        (400, 700),   # Below minimum
    ]
    
    for width, height in test_dimensions:
        is_compatible, aspect_match, quality_score, quality_tier = scraper.is_social_media_compatible(width, height)
        
        status = "✅ ACCEPT" if is_compatible else "❌ REJECT"
        print(f"{status} {width}x{height} - ", end="")
        
        if is_compatible:
            tier_emoji = "🔥" if quality_tier == "perfect" else "✂️"
            print(f"{aspect_match} ({tier_emoji} {quality_tier}, Score: {quality_score})")
        else:
            print("Not compatible")
    
    scraper.close()
    print("\n✅ Dimension compatibility test complete!")

if __name__ == "__main__":
    test_url_conversion()
    test_dimension_check()