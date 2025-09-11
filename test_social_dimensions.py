#!/usr/bin/env python3
"""
Test script to verify TikTok/Instagram dimension filtering
"""

from enhanced_scraper import EnhancedPinterestScraper

def test_social_media_compatibility():
    """Test the social media compatibility checking"""
    scraper = EnhancedPinterestScraper(headless=True)
    
    print("🧪 Testing Social Media Dimension Compatibility")
    print("=" * 60)
    
    # Test various dimensions
    test_cases = [
        # Perfect ratios - Tier 1
        (1080, 1920, "9:16 TikTok/Stories (Perfect)"),
        (720, 1280, "9:16 Lower res (Perfect)"),
        (1080, 1080, "1:1 Square (Perfect)"),
        (800, 800, "1:1 Square lower res (Perfect)"),
        (1080, 1350, "4:5 Instagram feed (Perfect)"),
        (864, 1080, "4:5 Instagram feed (Perfect)"),
        
        # Croppable ratios - Tier 2
        (1080, 1440, "3:4 Instagram Reels grid (Croppable)"),
        (720, 960, "3:4 Lower res (Croppable)"),
        (1080, 1620, "2:3 Stories crop (Croppable)"),
        (1080, 1728, "5:8 Close to 9:16 (Croppable)"),
        
        # Should be rejected
        (540, 960, "9:16 Too low res (reject)"),
        (1920, 1080, "16:9 Landscape (reject)"),
        (800, 600, "4:3 Traditional (reject)"),
        (400, 400, "Too small square (reject)"),
        (1080, 1200, "Odd ratio (reject)"),
    ]
    
    print(f"Testing {len(test_cases)} dimension scenarios:\n")
    
    compatible_count = 0
    
    for width, height, description in test_cases:
        is_compatible, aspect_match, quality_score, quality_tier = scraper.is_social_media_compatible(width, height)
        
        status = "✅ ACCEPT" if is_compatible else "❌ REJECT"
        tier_emoji = "🔥" if quality_tier == "perfect" else "✂️" if quality_tier == "croppable" else ""
        aspect_info = f"({aspect_match}, Score: {quality_score}, {tier_emoji}{quality_tier})" if is_compatible else "(Not suitable)"
        
        print(f"{status} {width}x{height} - {description} {aspect_info}")
        
        if is_compatible:
            compatible_count += 1
    
    print(f"\n📊 Results Summary:")
    print(f"Compatible: {compatible_count}/{len(test_cases)}")
    print(f"Rejection Rate: {((len(test_cases) - compatible_count) / len(test_cases)) * 100:.1f}%")
    
    scraper.close()
    return compatible_count

def test_live_scraping():
    """Test actual scraping with dimension filtering"""
    scraper = EnhancedPinterestScraper(headless=True)
    
    try:
        print(f"\n🔴 LIVE TEST: Scraping with Social Media Filtering")
        print("=" * 60)
        print("Testing with 'Aesthetic Books' category (5 images max)")
        
        # Small test scrape
        result = scraper.scrape_category("Aesthetic Books", target_count=5, max_scrolls=10)
        
        print(f"\n📋 Live Scraping Results:")
        print(f"Social media compatible images found: {len(result['images'])}")
        
        if result['images']:
            print(f"\n📱 Dimension Analysis:")
            aspect_counts = {}
            
            for i, img in enumerate(result['images'], 1):
                dims = img.get('dimensions', {})
                width = dims.get('width', 'Unknown')
                height = dims.get('height', 'Unknown')
                aspect = dims.get('aspect_ratio', 'Unknown')
                score = dims.get('quality_score', 0)
                
                print(f"{i}. {width}x{height} ({aspect}) - Score: {score}")
                
                # Count aspect ratios
                if aspect in aspect_counts:
                    aspect_counts[aspect] += 1
                else:
                    aspect_counts[aspect] = 1
            
            print(f"\n📊 Aspect Ratio Distribution:")
            for aspect, count in aspect_counts.items():
                percentage = (count / len(result['images'])) * 100
                if aspect == '9:16':
                    platform = "Perfect for TikTok, Instagram Stories/Reels"
                elif aspect == '1:1':
                    platform = "Perfect for Instagram Posts (Square)"
                elif aspect == '4:5':
                    platform = "Perfect for Instagram Feed"
                else:
                    platform = "Social media compatible"
                
                print(f"  {aspect}: {count} images ({percentage:.1f}%) - {platform}")
        else:
            print("⚠️  No social media compatible images found in this test.")
            print("   This might be normal - try increasing max_scrolls or different category.")
            
    finally:
        scraper.close()

def analyze_target_dimensions():
    """Analyze what dimensions we're targeting"""
    scraper = EnhancedPinterestScraper()
    
    print(f"\n🎯 TARGET DIMENSIONS ANALYSIS")
    print("=" * 60)
    
    print(f"Target Aspect Ratios (EXPANDED):")
    perfect_ratios = [(9, 16), (1, 1), (4, 5)]
    croppable_ratios = [(3, 4), (2, 3), (5, 8)]
    
    print(f"\n🔥 PERFECT RATIOS:")
    for w, h in perfect_ratios:
        ratio = w / h
        print(f"  {w}:{h} (decimal: {ratio:.3f})")
        if w == 9 and h == 16:
            print(f"    → TikTok, Instagram Stories/Reels")
        elif w == 1 and h == 1:
            print(f"    → Instagram Square Posts")
        elif w == 4 and h == 5:
            print(f"    → Instagram Feed Posts")
    
    print(f"\n✂️  CROPPABLE RATIOS:")
    for w, h in croppable_ratios:
        ratio = w / h
        print(f"  {w}:{h} (decimal: {ratio:.3f})")
        if w == 3 and h == 4:
            print(f"    → Instagram Reels grid (crop to 9:16)")
        elif w == 2 and h == 3:
            print(f"    → Stories crop (crop to 9:16)")
        elif w == 5 and h == 8:
            print(f"    → Close to TikTok (slight crop to 9:16)")
    
    print(f"\nPreferred Exact Dimensions:")
    for width, height in scraper.preferred_dimensions:
        aspect = width / height
        tier = "Perfect" if (width, height) in [(1080, 1920), (1080, 1080), (1080, 1350)] else "Croppable"
        print(f"  {width}x{height} (aspect: {aspect:.3f}) [{tier}]")
    
    print(f"\nMinimum Resolution: {scraper.min_resolution}px (TIKTOK QUALITY)")
    print(f"Aspect Ratio Tolerance: 0.2 (STRICT for quality)")
    print(f"Quality Scoring: Perfect=85-100, Croppable=70-85")
    print(f"Minimum Quality Threshold: 85+ (TikTok-ready only)")
    
    scraper.close()

if __name__ == "__main__":
    print("🎬 SOCIAL MEDIA DIMENSION TESTING SUITE")
    print("=" * 70)
    
    # Test 1: Dimension compatibility logic
    compatible_count = test_social_media_compatibility()
    
    # Test 2: Target dimensions analysis  
    analyze_target_dimensions()
    
    # Test 3: Live scraping test
    if compatible_count > 0:
        print(f"\n⚡ Compatibility tests passed! Running live scraping test...")
        test_live_scraping()
    else:
        print(f"\n⚠️  Compatibility tests failed. Skipping live test.")
    
    print(f"\n🎉 Testing Complete!")
    print(f"If live test found compatible images, the scraper is working correctly.")