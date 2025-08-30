#!/usr/bin/env python3
"""
Pinterest Image Scraper - Main Entry Point

This scraper bypasses API limits by:
1. Using Selenium for browser automation (no API needed)
2. Implementing human-like scrolling patterns
3. Adding random delays and breaks
4. Rotating user agents and window sizes
5. Extracting high-resolution image URLs directly
"""

from enhanced_scraper import EnhancedPinterestScraper
from image_url_scraper import scrape_image_urls_only

def quick_scrape_demo():
    """Quick demo to scrape a few images from each category"""
    categories = [
        "Entrepreneur",
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
    
    print("🚀 Starting Pinterest Image URL Scraper")
    print("=" * 50)
    print("This will scrape image URLs only (no downloading)")
    print("=" * 50)
    
    # Scrape just URLs
    urls = scrape_image_urls_only(categories, images_per_category=30)
    
    # Display results
    print("\n📋 Results Summary:")
    total = 0
    for category, url_list in urls.items():
        count = len(url_list)
        total += count
        print(f"  • {category}: {count} images")
        if url_list:
            print(f"    Sample URL: {url_list[0][:80]}...")
    
    print(f"\n✨ Total images found: {total}")
    print("📁 URLs saved to: findings/ (organized by category)")

def full_scrape_with_metadata():
    """Full scrape with all metadata"""
    categories = [
        "Entrepreneur",
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
    
    scraper = EnhancedPinterestScraper(headless=False)
    
    try:
        # Scrape all categories with full metadata
        results = scraper.scrape_multiple_categories(
            categories, 
            images_per_category=50
        )
        
        # Save comprehensive results
        scraper.save_results('pinterest_full_data.json', {
            'categories': results,
            'total_images': sum(len(r['images']) for r in results)
        })
        
        # Export to CSV for easy viewing
        scraper.export_to_csv('pinterest_images_full.csv')
        
        print("\n✅ Full scraping completed!")
        
    finally:
        scraper.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--full":
        print("Running full scrape with metadata...")
        full_scrape_with_metadata()
    else:
        print("Running quick URL-only scrape...")
        quick_scrape_demo()
