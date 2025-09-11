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
from s3_uploader import S3Uploader
import sys
from pathlib import Path

def quick_scrape_demo():
    """Quick demo to scrape a few images from each category"""
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

def upload_to_s3(category_name: str = None):
    """Upload 9x16 images to S3 bucket"""
    print("☁️  S3 Upload Tool")
    print("=" * 50)
    
    try:
        # Initialize S3 uploader
        uploader = S3Uploader()
        
        # Test connection
        print("Testing S3 connection...")
        if not uploader.test_connection():
            print("❌ Failed to connect to S3. Check your credentials.")
            return
        
        print("✅ S3 connection successful!")
        
        # Get available categories
        available_categories = uploader.list_available_categories()
        
        if not available_categories:
            print("❌ No categories with 9x16 images found in findings/ directory")
            return
        
        print(f"\n📁 Available categories: {', '.join(available_categories)}")
        
        # Determine which categories to upload
        if category_name:
            if category_name not in available_categories:
                print(f"❌ Category '{category_name}' not found or has no 9x16 images")
                return
            categories_to_upload = [category_name]
        else:
            categories_to_upload = available_categories
        
        # Upload each category
        total_stats = {"uploaded": 0, "skipped": 0, "errors": 0}
        
        for cat in categories_to_upload:
            print(f"\n📤 Uploading category: {cat}")
            print("-" * 30)
            
            # Get local file count
            local_stats = uploader.get_category_stats(cat)
            print(f"Local files: {local_stats['local_files']}")
            
            # Upload images
            stats = uploader.upload_category_images(cat)
            
            # Display results
            print(f"✅ Uploaded: {stats['uploaded']}")
            print(f"⏭️  Skipped: {stats['skipped']}")
            print(f"❌ Errors: {stats['errors']}")
            
            # Update totals
            for key in total_stats:
                total_stats[key] += stats[key]
        
        # Final summary
        print(f"\n🎉 Upload Complete!")
        print("=" * 50)
        print(f"Total uploaded: {total_stats['uploaded']}")
        print(f"Total skipped: {total_stats['skipped']}")
        print(f"Total errors: {total_stats['errors']}")
        print(f"\n📂 Images stored in: s3://tryfaceless/library/[category-name]/")
        
    except Exception as e:
        print(f"❌ Error during upload: {e}")

def list_categories():
    """List all available categories with file counts"""
    print("📁 Available Categories")
    print("=" * 50)
    
    try:
        uploader = S3Uploader()
        categories = uploader.list_available_categories()
        
        if not categories:
            print("❌ No categories found in findings/ directory")
            return
        
        for category in categories:
            stats = uploader.get_category_stats(category)
            print(f"  • {category}: {stats['local_files']} images")
        
        print(f"\nTotal categories: {len(categories)}")
        
    except Exception as e:
        print(f"❌ Error listing categories: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "--full":
            print("Running full scrape with metadata...")
            full_scrape_with_metadata()
        elif command == "--upload":
            # Upload specific category or all
            category = sys.argv[2] if len(sys.argv) > 2 else None
            upload_to_s3(category)
        elif command == "--list":
            list_categories()
        elif command == "--help":
            print("Pinterest Scraper - Available Commands:")
            print("  python main.py                    - Quick URL-only scrape")
            print("  python main.py --full             - Full scrape with metadata")
            print("  python main.py --upload           - Upload all categories to S3")
            print("  python main.py --upload [category] - Upload specific category to S3")
            print("  python main.py --list             - List available categories")
            print("  python main.py --help             - Show this help")
        else:
            print(f"Unknown command: {command}")
            print("Use --help to see available commands")
    else:
        print("Running quick URL-only scrape...")
        quick_scrape_demo()
