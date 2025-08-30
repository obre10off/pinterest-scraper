#!/usr/bin/env python3
"""
Utility to download images from scraped URLs
Run this after scraping to actually download the images
"""

import os
import json
import requests
import time
from pathlib import Path

def download_image(url, filepath):
    """Download a single image from URL"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return True
    except Exception as e:
        print(f"Error downloading: {e}")
    return False

def download_category_images(category_folder, max_images=None):
    """Download images for a specific category"""
    # Look for URLs file
    urls_file = f"findings/{category_folder}/urls_only.txt"
    json_file = f"findings/{category_folder}/image_data.json"
    
    urls = []
    
    # Try to load URLs from text file
    if os.path.exists(urls_file):
        with open(urls_file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.strip() and not line.startswith('#'):
                    # Extract URL from numbered list format
                    parts = line.split('. ', 1)
                    if len(parts) > 1:
                        urls.append(parts[1].strip())
    
    # Or try JSON file
    elif os.path.exists(json_file):
        with open(json_file, 'r') as f:
            data = json.load(f)
            urls = [img['image_url'] for img in data.get('images', [])]
    
    if not urls:
        print(f"No URLs found for {category_folder}")
        return 0
    
    # Create images subfolder
    images_folder = f"findings/{category_folder}/images"
    os.makedirs(images_folder, exist_ok=True)
    
    # Download images
    downloaded = 0
    total = min(len(urls), max_images) if max_images else len(urls)
    
    print(f"\nDownloading {total} images for {category_folder}...")
    
    for i, url in enumerate(urls[:total], 1):
        ext = 'jpg' if 'jpg' in url.lower() else 'png'
        filepath = f"{images_folder}/img_{i:04d}.{ext}"
        
        if download_image(url, filepath):
            downloaded += 1
            print(f"  [{downloaded}/{total}] Downloaded: img_{i:04d}.{ext}")
        else:
            print(f"  [FAILED] Could not download image {i}")
        
        # Rate limiting
        time.sleep(1)
    
    return downloaded

def download_all_categories(max_per_category=50):
    """Download images for all categories"""
    findings_dir = Path("findings")
    
    if not findings_dir.exists():
        print("No findings directory found. Run the scraper first!")
        return
    
    # Find all category folders
    categories = [d for d in findings_dir.iterdir() if d.is_dir()]
    
    if not categories:
        print("No category folders found in findings/")
        return
    
    print(f"Found {len(categories)} categories to download")
    total_downloaded = 0
    
    for category_path in categories:
        category = category_path.name
        downloaded = download_category_images(category, max_per_category)
        total_downloaded += downloaded
        print(f"✅ Downloaded {downloaded} images for {category}\n")
    
    print(f"\n🎉 Total images downloaded: {total_downloaded}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Download specific category
        category = sys.argv[1]
        max_images = int(sys.argv[2]) if len(sys.argv) > 2 else None
        download_category_images(category, max_images)
    else:
        # Download all categories
        print("Downloading images for all categories...")
        print("(Use 'python download_images.py category_name [max]' for specific category)")
        download_all_categories(max_per_category=30)