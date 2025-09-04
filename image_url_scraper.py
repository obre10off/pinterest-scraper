import json
import time
import random
from enhanced_scraper import EnhancedPinterestScraper

def scrape_image_urls_only(categories, images_per_category=50):
    """
    Simple function to scrape just image URLs for given categories
    Returns a dictionary with categories as keys and lists of image URLs as values
    """
    import os
    
    scraper = EnhancedPinterestScraper(headless=False)
    all_urls = {}
    
    try:
        for category in categories:
            print(f"\n🔍 Scraping URLs for: {category}")
            # Increase max_scrolls significantly for better yield
            result = scraper.scrape_category(category, images_per_category, max_scrolls=100)
            
            # Extract just the image URLs
            urls = [img['image_url'] for img in result['images']]
            all_urls[category] = urls
            
            # Save URLs in category folder
            category_folder = category.replace(' ', '_').lower()
            folder_path = f'findings/{category_folder}'
            os.makedirs(folder_path, exist_ok=True)
            
            # Save URLs to text file in category folder
            with open(f'{folder_path}/urls_only.txt', 'w') as f:
                for i, url in enumerate(urls, 1):
                    f.write(f"{i}. {url}\n")
            
            print(f"✅ Found {len(urls)} image URLs for {category}")
            print(f"📁 Saved to findings/{category_folder}/")
            
            # Small delay between categories
            if category != categories[-1]:
                time.sleep(random.uniform(5, 10))
        
        # Save master URLs file in findings root
        os.makedirs('findings', exist_ok=True)
        with open('findings/all_image_urls.json', 'w') as f:
            json.dump(all_urls, f, indent=2)
        
        print(f"\n📊 Total URLs scraped: {sum(len(urls) for urls in all_urls.values())}")
        return all_urls
        
    finally:
        scraper.close()

if __name__ == "__main__":
    # Your categories
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
    
    # Scrape URLs only (no downloading)
    urls = scrape_image_urls_only(categories, images_per_category=50)
    
    # Print summary
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    for category, url_list in urls.items():
        print(f"{category}: {len(url_list)} URLs")