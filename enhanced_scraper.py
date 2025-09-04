from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import json
import random
import os
from urllib.parse import quote
from datetime import datetime
import csv
import requests
from PIL import Image
from io import BytesIO

class EnhancedPinterestScraper:
    def __init__(self, headless=False):
        """Initialize scraper with anti-detection measures"""
        
        # Social media optimal dimensions - EXPANDED for better yield
        self.target_aspect_ratios = [
            # Perfect ratios
            (9, 16),  # TikTok, Instagram Stories/Reels (1080x1920)
            (1, 1),   # Square format (1080x1080) 
            (4, 5),   # Instagram feed optimal (1080x1350)
            
            # Easily croppable ratios
            (3, 4),   # Instagram Reels grid, very close to 4:5 (1080x1440)
            (2, 3),   # Between 4:5 and 9:16, good for Stories (1080x1620) 
            (5, 8),   # Close to 9:16, easily croppable (1080x1728)
        ]
        self.min_resolution = 500  # Significantly reduced for better yield
        self.preferred_dimensions = [
            (1080, 1920), (1080, 1080), (1080, 1350),  # Perfect
            (1080, 1440), (1080, 1620), (1080, 1728)   # Croppable
        ]
        options = webdriver.ChromeOptions()
        
        # Anti-detection measures
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        
        # Randomize window size
        window_sizes = [(1920, 1080), (1366, 768), (1440, 900)]
        width, height = random.choice(window_sizes)
        options.add_argument(f'--window-size={width},{height}')
        
        # Random user agent
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        options.add_argument(f'user-agent={random.choice(user_agents)}')
        
        if headless:
            options.add_argument('--headless')
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 15)
        self.scraped_data = []
        
        # Execute stealth JavaScript
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    def human_like_scroll(self):
        """Simulate human-like scrolling behavior with better image loading"""
        # Get current scroll position and height
        scroll_height = self.driver.execute_script("return document.body.scrollHeight")
        current_position = self.driver.execute_script("return window.pageYOffset")
        
        # Multiple small scrolls to trigger lazy loading
        for _ in range(3):
            scroll_distance = random.randint(200, 400)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_distance})")
            time.sleep(random.uniform(0.3, 0.7))
        
        # Final scroll to ensure we reach new content
        self.driver.execute_script(f"window.scrollTo(0, {scroll_height})")
        
        # Wait for images to load
        time.sleep(random.uniform(2.0, 3.5))
    
    def get_image_dimensions(self, url):
        """Get image dimensions by downloading headers/partial content"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # Try to get dimensions from image headers first
            response = requests.head(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # Download a small portion to get dimensions
                response = requests.get(url, headers=headers, stream=True, timeout=10)
                if response.status_code == 200:
                    # Read just enough to get image dimensions
                    img_data = BytesIO()
                    downloaded = 0
                    for chunk in response.iter_content(1024):
                        img_data.write(chunk)
                        downloaded += len(chunk)
                        
                        # Try to get dimensions after each chunk
                        try:
                            img_data.seek(0)
                            with Image.open(img_data) as img:
                                return img.size  # (width, height)
                        except:
                            pass
                        
                        # Don't download more than 50KB for dimension detection
                        if downloaded > 50000:
                            break
                            
        except Exception as e:
            print(f"Error getting dimensions for {url}: {e}")
        
        return None
    
    def is_social_media_compatible(self, width, height):
        """Check if image dimensions are suitable for TikTok/Instagram - TWO TIER SYSTEM"""
        if not width or not height:
            return False, None, 0, None
        
        # More relaxed minimum resolution requirement
        if max(width, height) < self.min_resolution * 0.8:  # Below 80% of minimum (400px)
            return False, None, 0, None
        
        # Calculate aspect ratio
        aspect_ratio = width / height
        
        # Check against target ratios with significantly expanded tolerance
        tolerance = 0.35  # Significantly increased for better yield
        best_match = None
        best_score = 0
        quality_tier = None
        
        # Perfect ratios (Tier 1)
        perfect_ratios = [(9, 16), (1, 1), (4, 5)]
        # Croppable ratios (Tier 2) 
        croppable_ratios = [(3, 4), (2, 3), (5, 8)]
        
        for target_w, target_h in self.target_aspect_ratios:
            target_ratio = target_w / target_h
            
            if abs(aspect_ratio - target_ratio) <= tolerance:
                # Calculate quality score based on how close to preferred dimensions
                score = 0
                
                # Determine quality tier
                if (target_w, target_h) in perfect_ratios:
                    tier = "perfect"
                    base_score = 80  # Higher base score for perfect ratios
                else:
                    tier = "croppable" 
                    base_score = 60  # Lower base score for croppable ratios
                
                # Bonus for exact preferred dimensions
                if (width, height) in self.preferred_dimensions:
                    score = 100 if tier == "perfect" else 85
                elif (height, width) in self.preferred_dimensions:  # Check flipped
                    score = 100 if tier == "perfect" else 85
                else:
                    # Score based on resolution quality
                    min_dim = min(width, height)
                    max_dim = max(width, height)
                    
                    score = base_score
                    if min_dim >= 1080:
                        score += 15
                    elif min_dim >= 720:
                        score += 10
                    
                    # Bonus for higher resolution
                    if max_dim >= 1920:
                        score += 5
                    elif max_dim >= 1440:
                        score += 3
                
                if score > best_score:
                    best_score = score
                    best_match = f"{target_w}:{target_h}"
                    quality_tier = tier
        
        return best_match is not None, best_match, best_score, quality_tier
    
    def convert_to_original_url(self, url):
        """Convert Pinterest thumbnail URL to original high-res URL"""
        # Skip video thumbnails completely
        if '/videos/' in url or '.0000000.' in url or '.0000001.' in url:
            return None
            
        # Common Pinterest URL patterns:
        # https://i.pinimg.com/236x/xx/xx/xx/image.jpg -> originals
        # https://i.pinimg.com/474x/xx/xx/xx/image.jpg -> originals  
        # https://i.pinimg.com/736x/xx/xx/xx/image.jpg -> originals
        # https://i.pinimg.com/originals/xx/xx/xx/image.jpg (already original)
        
        # If already original and not a video, keep it
        if 'originals' in url:
            return url
        
        # Extract the hash and filename from the URL
        import re
        # Match various Pinterest thumbnail patterns
        patterns = [
            r'https://i\.pinimg\.com/\d+x/([a-f0-9]{2}/[a-f0-9]{2}/[a-f0-9]{2}/[^/]+)',
            r'https://i\.pinimg\.com/\d+x\d+/([a-f0-9]{2}/[a-f0-9]{2}/[a-f0-9]{2}/[^/]+)'
        ]
        
        for pattern in patterns:
            match = re.match(pattern, url)
            if match:
                # Construct the originals URL
                path = match.group(1)
                return f'https://i.pinimg.com/originals/{path}'
        
        # If we can't convert it, return None to skip this image
        return None
    
    def extract_image_data(self, img_element):
        """Extract comprehensive image data from element - SOCIAL MEDIA OPTIMIZED"""
        try:
            src = img_element.get_attribute('src')
            if not src or 'pinimg.com' not in src:
                return None
            
            # Skip profile pictures and very small thumbnails
            if '/60x60/' in src or '/75x75/' in src or '/140x/' in src:
                return None
            
            # Skip video thumbnails (additional check)
            if '/videos/' in src or '.0000000.' in src or '.0000001.' in src:
                return None
            
            # Convert thumbnail URLs to originals
            original_src = self.convert_to_original_url(src)
            
            # Skip if we couldn't convert to original URL
            if not original_src:
                return None
            
            # GET IMAGE DIMENSIONS for social media compatibility
            # Only print for successful finds
            # (printing moved to after success check)
            dimensions = self.get_image_dimensions(original_src)
            
            if not dimensions:
                # Don't print - this happens often
                return None
            
            width, height = dimensions
            is_compatible, aspect_match, quality_score, quality_tier = self.is_social_media_compatible(width, height)
            
            if not is_compatible:
                # Don't print - this happens very often
                return None
            
            tier_emoji = "🔥" if quality_tier == "perfect" else "✂️"
            print(f"✅ Found compatible image: {width}x{height} ({aspect_match}) - Score: {quality_score} [{tier_emoji} {quality_tier}]")
            # Show a sample of the URL to verify it's not a video
            if random.random() < 0.3:  # Show 30% of URLs
                print(f"   URL preview: {original_src[:80]}...")
            
            # Get metadata
            alt_text = img_element.get_attribute('alt') or ''
            
            pin_url = None
            try:
                parent = img_element.find_element(By.XPATH, './ancestor::a[@href]')
                pin_url = parent.get_attribute('href')
            except:
                pass
            
            return {
                'image_url': original_src,
                'thumbnail_url': src,
                'alt_text': alt_text,
                'pin_url': pin_url,
                'timestamp': datetime.now().isoformat(),
                'dimensions': {
                    'width': width,
                    'height': height,
                    'aspect_ratio': aspect_match,
                    'quality_score': quality_score,
                    'quality_tier': quality_tier
                }
            }
        except Exception as e:
            print(f"Error processing image: {e}")
            return None
    
    def scrape_category(self, category, target_count=100, max_scrolls=150):
        """Enhanced category scraping with improved yield strategy"""
        print(f"\n🎯 Scraping category: {category}")
        
        # URL encode the category
        encoded_category = quote(category)
        url = f"https://www.pinterest.com/search/pins/?q={encoded_category}"
        
        self.driver.get(url)
        time.sleep(random.uniform(3, 5))  # Initial load with random delay
        
        # Initial scroll to trigger image loading
        self.driver.execute_script("window.scrollBy(0, 500)")
        time.sleep(2)
        self.driver.execute_script("window.scrollBy(0, 500)")
        time.sleep(2)
        
        # Wait for actual pin images to appear (not just profile pics)
        attempts = 0
        while attempts < 5:
            test_imgs = self.driver.find_elements(By.CSS_SELECTOR, 
                "img[src*='/236x/'], img[src*='/474x/'], img[src*='/736x/'], img[src*='/564x/'], img[src*='/originals/']")
            if len(test_imgs) > 0:
                print(f"👍 Found {len(test_imgs)} pin images ready")
                break
            print(f"⏳ Waiting for images to load (attempt {attempts+1}/5)...")
            self.driver.execute_script("window.scrollBy(0, 1000)")
            time.sleep(3)
            attempts += 1
        
        scraped_images = {}
        no_new_images_count = 0
        scroll_count = 0
        
        while len(scraped_images) < target_count and scroll_count < max_scrolls:
            # Find all image elements (exclude profile pictures)
            img_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                "img[src*='pinimg.com']:not([src*='/60x60/']):not([src*='/75x75/'])")
            
            initial_count = len(scraped_images)
            
            for img in img_elements:
                if len(scraped_images) >= target_count:
                    break
                
                try:
                    # Get the src to check if we've processed it
                    src = img.get_attribute('src')
                    if not src:
                        continue
                    
                    img_data = self.extract_image_data(img)
                    if img_data and img_data['image_url'] not in scraped_images:
                        scraped_images[img_data['image_url']] = img_data
                except Exception as e:
                    # Handle stale element errors gracefully - don't print
                    if "stale element" in str(e).lower():
                        continue
                    else:
                        # Only print errors occasionally to reduce noise
                        if random.random() < 0.05:  # 5% of errors
                            print(f"⚠️  Error processing image: {str(e)[:50]}")
                        continue
            
            # Check if we found new images
            if len(scraped_images) == initial_count:
                no_new_images_count += 1
                if no_new_images_count > 15:  # Increased patience from 5 to 15
                    print(f"⚠️  No new compatible images found after {no_new_images_count} attempts. Moving on...")
                    break
            else:
                no_new_images_count = 0
            
            print(f"📊 Progress: {len(scraped_images)}/{target_count} images (Scroll {scroll_count}/{max_scrolls})")
            
            # Human-like scrolling
            self.human_like_scroll()
            scroll_count += 1
            
            # Occasional longer pause to avoid rate limiting
            if scroll_count % 10 == 0:
                print("⏸️  Taking a break to avoid rate limiting...")
                time.sleep(random.uniform(5, 10))
        
        # Store results
        category_data = {
            'category': category,
            'images': list(scraped_images.values())[:target_count],
            'total_found': len(scraped_images)
        }
        
        self.scraped_data.append(category_data)
        
        # Automatically save results
        if category_data['images']:
            self.save_results(f"image_data.json", category_data, category=category)
            self.save_urls_to_txt(category_data['images'], category)
        
        return category_data
    
    def scrape_multiple_categories(self, categories, images_per_category=50):
        """Scrape multiple categories with breaks between them"""
        all_results = []
        
        for i, category in enumerate(categories):
            print(f"\n{'='*50}")
            print(f"Processing {i+1}/{len(categories)}: {category}")
            print(f"{'='*50}")
            
            try:
                result = self.scrape_category(category, images_per_category)
                all_results.append(result)
                
                # Save intermediate results in category folder
                self.save_results(f"image_data.json", result, category=category)
                
                # Also save just URLs in a simple text file
                self.save_urls_to_txt(result['images'], category)
                
                # Take a break between categories
                if i < len(categories) - 1:
                    break_time = random.uniform(10, 20)
                    print(f"\n⏰ Taking {break_time:.1f} second break before next category...")
                    time.sleep(break_time)
                    
            except Exception as e:
                print(f"❌ Error scraping {category}: {e}")
                continue
        
        return all_results
    
    def save_results(self, filename, data, category=None):
        """Save scraped data to JSON file in organized folders"""
        if category:
            # Save in findings/category_name/ folder
            category_folder = category.replace(' ', '_').lower()
            folder_path = f'findings/{category_folder}'
            os.makedirs(folder_path, exist_ok=True)
            filepath = f'{folder_path}/{filename}'
        else:
            # Save in findings root for summary files
            os.makedirs('findings', exist_ok=True)
            filepath = f'findings/{filename}'
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved data to {filepath}")
    
    def export_to_csv(self, filename='pinterest_images.csv'):
        """Export all scraped data to CSV"""
        os.makedirs('findings', exist_ok=True)
        filepath = f'findings/{filename}'
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Category', 'Image URL', 'Thumbnail URL', 'Alt Text', 'Pin URL', 'Timestamp'])
            
            for category_data in self.scraped_data:
                category = category_data['category']
                for img in category_data['images']:
                    writer.writerow([
                        category,
                        img['image_url'],
                        img['thumbnail_url'],
                        img['alt_text'],
                        img['pin_url'],
                        img['timestamp']
                    ])
        
        print(f"📊 Exported data to {filepath}")
    
    def save_urls_to_txt(self, images, category):
        """Save image URLs organized by quality tier and aspect ratio"""
        category_folder = category.replace(' ', '_').lower()
        base_folder = f'findings/{category_folder}'
        os.makedirs(base_folder, exist_ok=True)
        
        # Organize images by quality tier and aspect ratio
        perfect_images = []
        croppable_images = []
        
        for img in images:
            if 'dimensions' in img and 'quality_tier' in img['dimensions']:
                if img['dimensions']['quality_tier'] == 'perfect':
                    perfect_images.append(img)
                else:
                    croppable_images.append(img)
            else:
                # Fallback - assume croppable if no tier info
                croppable_images.append(img)
        
        # Further organize by aspect ratio within each tier
        perfect_by_aspect = {}
        croppable_by_aspect = {}
        
        for img in perfect_images:
            aspect = img['dimensions']['aspect_ratio'] if 'dimensions' in img else 'unknown'
            if aspect not in perfect_by_aspect:
                perfect_by_aspect[aspect] = []
            perfect_by_aspect[aspect].append(img)
            
        for img in croppable_images:
            aspect = img['dimensions']['aspect_ratio'] if 'dimensions' in img else 'unknown'
            if aspect not in croppable_by_aspect:
                croppable_by_aspect[aspect] = []
            croppable_by_aspect[aspect].append(img)
        
        # Save overall summary
        summary_path = f'{base_folder}/social_media_urls.txt'
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(f"# TikTok/Instagram Optimized URLs for {category}\n")
            f.write(f"# Total: {len(images)} social-media-ready images\n")
            f.write(f"# Perfect: {len(perfect_images)} | Croppable: {len(croppable_images)}\n")
            f.write("#" + "="*70 + "\n\n")
            
            # Perfect images section
            if perfect_images:
                f.write(f"## 🔥 PERFECT IMAGES ({len(perfect_images)} images)\n")
                f.write(f"# Ready to use directly - no cropping needed!\n")
                f.write("#" + "-"*50 + "\n")
                
                for aspect_ratio, group_images in perfect_by_aspect.items():
                    f.write(f"### {aspect_ratio.upper()} ({len(group_images)} images)\n")
                    if aspect_ratio == '9:16':
                        f.write("# Perfect for: TikTok, Instagram Stories/Reels\n")
                    elif aspect_ratio == '1:1':
                        f.write("# Perfect for: Instagram Posts (Square)\n")
                    elif aspect_ratio == '4:5':
                        f.write("# Perfect for: Instagram Feed Posts\n")
                    
                    for i, img in enumerate(group_images, 1):
                        dimensions = img.get('dimensions', {})
                        width = dimensions.get('width', 'Unknown')
                        height = dimensions.get('height', 'Unknown')
                        score = dimensions.get('quality_score', 0)
                        f.write(f"{i}. {img['image_url']} ({width}x{height}, Score: {score})\n")
                    f.write("\n")
            
            # Croppable images section
            if croppable_images:
                f.write(f"## ✂️ CROPPABLE IMAGES ({len(croppable_images)} images)\n")
                f.write(f"# High quality - may need slight cropping for perfect fit\n")
                f.write("#" + "-"*50 + "\n")
                
                for aspect_ratio, group_images in croppable_by_aspect.items():
                    f.write(f"### {aspect_ratio.upper()} ({len(group_images)} images)\n")
                    if aspect_ratio == '3:4':
                        f.write("# Good for: Instagram Reels (slight crop to 9:16)\n")
                    elif aspect_ratio == '2:3':
                        f.write("# Good for: Instagram Stories (crop to 9:16)\n")
                    elif aspect_ratio == '5:8':
                        f.write("# Good for: TikTok (slight crop to 9:16)\n")
                    
                    for i, img in enumerate(group_images, 1):
                        dimensions = img.get('dimensions', {})
                        width = dimensions.get('width', 'Unknown')
                        height = dimensions.get('height', 'Unknown')
                        score = dimensions.get('quality_score', 0)
                        f.write(f"{i}. {img['image_url']} ({width}x{height}, Score: {score})\n")
                    f.write("\n")
        
        # Save separate files for perfect vs croppable
        if perfect_images:
            perfect_folder = f"{base_folder}/perfect"
            os.makedirs(perfect_folder, exist_ok=True)
            
            # Perfect images by aspect ratio
            for aspect_ratio, group_images in perfect_by_aspect.items():
                if aspect_ratio != 'unknown':
                    aspect_folder = f"{perfect_folder}/{aspect_ratio.replace(':', 'x')}"
                    os.makedirs(aspect_folder, exist_ok=True)
                    
                    aspect_file = f"{aspect_folder}/urls_only.txt"
                    with open(aspect_file, 'w', encoding='utf-8') as f:
                        for i, img in enumerate(group_images, 1):
                            f.write(f"{i}. {img['image_url']}\n")
                    
                    print(f"🔥 Saved {len(group_images)} perfect {aspect_ratio} images to {aspect_folder}/")
        
        if croppable_images:
            croppable_folder = f"{base_folder}/croppable"
            os.makedirs(croppable_folder, exist_ok=True)
            
            # Croppable images by aspect ratio
            for aspect_ratio, group_images in croppable_by_aspect.items():
                if aspect_ratio != 'unknown':
                    aspect_folder = f"{croppable_folder}/{aspect_ratio.replace(':', 'x')}"
                    os.makedirs(aspect_folder, exist_ok=True)
                    
                    aspect_file = f"{aspect_folder}/urls_only.txt"
                    with open(aspect_file, 'w', encoding='utf-8') as f:
                        for i, img in enumerate(group_images, 1):
                            f.write(f"{i}. {img['image_url']}\n")
                    
                    print(f"✂️  Saved {len(group_images)} croppable {aspect_ratio} images to {aspect_folder}/")
        
        print(f"📊 Saved social media summary to {summary_path}")
        print(f"🎯 Found {len(perfect_images)} perfect + {len(croppable_images)} croppable = {len(images)} total social media ready images")
    
    def close(self):
        """Clean up and close browser"""
        if self.driver:
            self.driver.quit()

def main():
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
    
    # Initialize scraper
    scraper = EnhancedPinterestScraper(headless=False)
    
    try:
        # Scrape all categories
        results = scraper.scrape_multiple_categories(
            categories, 
            images_per_category=50  # Adjust as needed
        )
        
        # Save all results to a master file
        scraper.save_results('all_pinterest_data.json', {
            'categories': results,
            'total_images': sum(len(r['images']) for r in results),
            'timestamp': datetime.now().isoformat()
        })
        
        # Export to CSV for easy viewing
        scraper.export_to_csv()
        
        print("\n✅ Scraping completed successfully!")
        print(f"📊 Total images scraped: {sum(len(r['images']) for r in results)}")
        
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
    finally:
        scraper.close()

if __name__ == "__main__":
    main()