#!/usr/bin/env python3
"""
Run the improved scraper on all original categories
"""

from enhanced_scraper import EnhancedPinterestScraper


categories = [
    "Entrepreneur Aesthetic",
    "Selfie Couples",
    "Laptop Study",
    "NYC Lifestyle",
    "Faceless Selfies",
    "Surrealism",
    "Fall Evening",
    "Summer Lake",
    "School",
    "Burning",
    "Gym",
    "Aesthetic Books"
]

print("🚀 Running Improved Pinterest Scraper")
print("=" * 60)

scraper = EnhancedPinterestScraper(headless=True)  # Use headless for speed
total_images = 0
results = {}

try:
    for i, category in enumerate(categories, 1):
        print(f"\n[{i}/{len(categories)}] Scraping: {category}")
        print("-" * 40)
        
        # Scrape with moderate settings
        result = scraper.scrape_category(category, target_count=20, max_scrolls=50)
        
        found = len(result['images'])
        total_images += found
        results[category] = found
        
        # Results are automatically saved by scrape_category
        
        print(f"✅ Completed: {found} images found")
        
        # Show a sample URL if found
        if result['images']:
            sample_url = result['images'][0]['image_url']
            if '/videos/' not in sample_url and '.0000000.' not in sample_url:
                print(f"   Sample: {sample_url[:70]}...")
            else:
                print("   ⚠️ First result was a video, checking for non-videos...")
                for img in result['images']:
                    url = img['image_url']
                    if '/videos/' not in url and '.0000000.' not in url:
                        print(f"   Sample: {url[:70]}...")
                        break
    
    print("\n" + "=" * 60)
    print("📊 FINAL RESULTS")
    print("=" * 60)
    
    for category, count in results.items():
        status = "✅" if count > 0 else "❌"
        bar = "█" * min(count, 20)
        print(f"{status} {category:20} {count:3} images {bar}")
    
    print(f"\n🎯 Total images scraped: {total_images}")
    
    # Calculate success rate
    successful_categories = sum(1 for count in results.values() if count > 0)
    success_rate = (successful_categories / len(categories)) * 100
    
    print(f"📈 Success rate: {success_rate:.1f}% ({successful_categories}/{len(categories)} categories)")
    
    if total_images > 100:
        print("\n🎉 Excellent! The improved scraper is working very well!")
    elif total_images > 50:
        print("\n✅ Good results! The scraper improvements are effective.")
    elif total_images > 20:
        print("\n⚠️ Moderate results. Some categories may have limited content.")
    else:
        print("\n❌ Low yield. May need to adjust search terms or settings.")
        
finally:
    scraper.close()
    print("\n✅ Scraping complete! Check the 'findings' folder for results.")