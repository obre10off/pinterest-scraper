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

class EnhancedPinterestScraper:
    def __init__(self, headless=False):
        """Initialize scraper with anti-detection measures"""
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
        """Simulate human-like scrolling behavior"""
        # Random scroll patterns
        scroll_pause = random.uniform(1.5, 3.0)
        
        # Sometimes scroll up a bit before scrolling down
        if random.random() > 0.7:
            self.driver.execute_script(f"window.scrollBy(0, -{random.randint(100, 300)})")
            time.sleep(random.uniform(0.5, 1.0))
        
        # Main scroll down
        scroll_height = random.randint(300, 700)
        self.driver.execute_script(f"window.scrollBy(0, {scroll_height})")
        time.sleep(scroll_pause)
    
    def extract_image_data(self, img_element):
        """Extract comprehensive image data from element"""
        try:
            src = img_element.get_attribute('src')
            if not src or 'pinimg.com' not in src:
                return None
            
            # Get various resolutions
            original_src = src
            if '236x' in src:
                original_src = src.replace('236x', 'originals')
            elif '474x' in src:
                original_src = src.replace('474x', 'originals')
            elif '736x' in src:
                original_src = src.replace('736x', 'originals')
            
            # Try to get alt text for context
            alt_text = img_element.get_attribute('alt') or ''
            
            # Try to get parent link for pin URL
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
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return None
    
    def scrape_category(self, category, target_count=100, max_scrolls=50):
        """Enhanced category scraping with better limit handling"""
        print(f"\n🎯 Scraping category: {category}")
        
        # URL encode the category
        encoded_category = quote(category)
        url = f"https://www.pinterest.com/search/pins/?q={encoded_category}"
        
        self.driver.get(url)
        time.sleep(random.uniform(3, 5))  # Initial load with random delay
        
        scraped_images = {}
        no_new_images_count = 0
        scroll_count = 0
        
        while len(scraped_images) < target_count and scroll_count < max_scrolls:
            # Find all image elements
            img_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                "img[src*='pinimg.com']")
            
            initial_count = len(scraped_images)
            
            for img in img_elements:
                if len(scraped_images) >= target_count:
                    break
                    
                img_data = self.extract_image_data(img)
                if img_data and img_data['image_url'] not in scraped_images:
                    scraped_images[img_data['image_url']] = img_data
            
            # Check if we found new images
            if len(scraped_images) == initial_count:
                no_new_images_count += 1
                if no_new_images_count > 5:
                    print(f"⚠️  No new images found after 5 scrolls. Moving on...")
                    break
            else:
                no_new_images_count = 0
            
            print(f"📊 Progress: {len(scraped_images)}/{target_count} images")
            
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
        """Save image URLs to a simple text file"""
        category_folder = category.replace(' ', '_').lower()
        folder_path = f'findings/{category_folder}'
        os.makedirs(folder_path, exist_ok=True)
        
        filepath = f'{folder_path}/image_urls.txt'
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# Image URLs for {category}\n")
            f.write(f"# Total: {len(images)} images\n")
            f.write("#" + "="*50 + "\n\n")
            for i, img in enumerate(images, 1):
                f.write(f"{i}. {img['image_url']}\n")
        
        print(f"📝 Saved URLs to {filepath}")
    
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