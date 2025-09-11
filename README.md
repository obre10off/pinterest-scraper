# Pinterest Image Scraper

A Python-based web scraper that extracts Pinterest image URLs by category without using APIs. Uses browser automation to bypass rate limits and organize results by category.

## 🚀 Quick Start

```bash
# 1. Clone or download this project
# 2. Navigate to the project directory
cd pintrest-scraper

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the scraper
python main.py
```

## 📋 Prerequisites

### Required Software
- **Python 3.7+** - Programming language
- **Google Chrome** - Browser for automation (must be installed)
- **pip** - Python package manager

### Auto-Installed Dependencies
- `selenium` - Browser automation
- `requests` - HTTP requests for downloading

## 🔧 Setup Instructions

### Step 1: Install Python Dependencies
```bash
# Install required packages
pip install -r requirements.txt
```

### Step 2: Verify Setup
```bash
# Test if everything is working
python test_setup.py
```
This will check:
- ✅ Selenium installation
- ✅ Chrome browser availability  
- ✅ File system permissions

### Step 3: Run the Scraper
```bash
# Option A: Quick scrape (30 images per category, URLs only)
python main.py

# Option B: Full scrape with metadata (50 images per category)
python main.py --full
```

## 📁 Project Structure

After running, your project will look like this:

```
pintrest-scraper/
├── main.py                    # Main entry point
├── enhanced_scraper.py        # Core scraper logic
├── image_url_scraper.py       # Simple URL-only scraper
├── download_images.py         # Optional image downloader
├── test_setup.py             # Setup verification tool
├── requirements.txt          # Python dependencies
├── README.md                # This file
└── findings/                # ← CREATED AUTOMATICALLY
    ├── entrepreneur_aesthetic/
    │   ├── image_data.json      # Full metadata
    │   ├── image_urls.txt       # Formatted URL list  
    │   └── urls_only.txt        # Simple URL list
    ├── selfie_couples/
    │   └── (same structure)
    ├── laptop_study/
    │   └── (same structure)
    ├── nyc_lifestyle/
    ├── faceless_selfies/
    ├── surrealism/
    ├── fall_evening/
    ├── summer_lake/
    ├── school/
    ├── burning/
    ├── gym/
    ├── aesthetic_books/
    └── all_image_urls.json     # Master summary file
```

## 🎯 How It Works

### Step-by-Step Process:

1. **Browser Automation**
   - Opens Chrome browser with anti-detection settings
   - Navigates to Pinterest search for each category
   - Uses human-like scrolling patterns

2. **Image Discovery**
   - Scrolls through Pinterest search results
   - Finds image elements with `pinimg.com` URLs
   - Converts thumbnail URLs to high-resolution versions

3. **Data Organization**
   - Creates `findings/` folder structure
   - Saves URLs in multiple formats per category
   - Adds metadata like alt text and pin URLs

4. **Rate Limit Avoidance**
   - Random delays between actions (1-10 seconds)
   - Human-like scrolling patterns
   - Breaks between categories
   - Randomized browser settings

## 📊 Categories Scraped

The scraper targets these 12 categories:
- **Entrepreneur Aesthetic** - Business and startup content
- **Selfie Couples** - Couple photography
- **Laptop Study** - Study and workspace aesthetics
- **NYC Lifestyle** - New York City lifestyle
- **Faceless Selfies** - Anonymous self-photography
- **Surrealism** - Artistic surreal content
- **Fall Evening** - Autumn evening aesthetics
- **Summer Lake** - Lake and summer scenes
- **School** - Educational and school content
- **Burning** - Fire and burning imagery
- **Gym** - Fitness and workout content
- **Aesthetic Books** - Book photography and reading

## 🛠️ Usage Examples

### Basic Usage
```bash
# Scrape all categories (30 images each)
python main.py
```

### Advanced Usage
```bash
# Full scrape with complete metadata
python main.py --full

# Test setup before running
python test_setup.py

# Download actual images (optional, after scraping)
python download_images.py

# Download specific category only
python download_images.py entrepreneur 20
```

### Customizing Categories
Edit the `categories` list in `main.py` to change what gets scraped:

```python
categories = [
    "Your Custom Category",
    "Another Category",
    # Add or remove categories here
]
```

## 📄 Output Files

### Per Category:
- **`urls_only.txt`** - Simple numbered list of image URLs
- **`image_urls.txt`** - Formatted list with headers  
- **`image_data.json`** - Full metadata including alt text, pin URLs

### Summary Files:
- **`all_image_urls.json`** - Master file with all categories
- **`pinterest_images.csv`** - Spreadsheet-friendly format

### Sample URL Format:
```
https://i.pinimg.com/originals/ab/cd/ef/abcdef123456.jpg
```
(High-resolution originals, not thumbnails)

## ⚠️ Important Notes

### Legal & Ethical
- **Personal Use Only** - Don't use for commercial purposes
- **Respect Rate Limits** - Built-in delays prevent overloading Pinterest
- **Image Rights** - Images remain property of original creators

### Technical
- **Chrome Required** - Uses ChromeDriver for automation
- **Internet Connection** - Needs stable internet for scraping
- **Storage Space** - URLs files are small, but downloading images requires space
- **Runtime** - Full scrape takes 10-30 minutes depending on internet speed

### Troubleshooting
- **"Chrome not found"** → Install Google Chrome browser
- **"Module not found"** → Run `pip install -r requirements.txt`
- **"Permission denied"** → Check folder write permissions
- **Slow performance** → Normal, includes delays to avoid rate limiting

## 🔧 Configuration

### Adjust Images Per Category
Edit the numbers in `main.py`:
```python
images_per_category=30  # Change this number
```

### Enable Headless Mode
In `enhanced_scraper.py`, change:
```python
scraper = EnhancedPinterestScraper(headless=True)  # Runs without GUI
```

### Modify Categories
Update the `categories` list in any of the main files to scrape different topics.

---

**Created for educational purposes. Use responsibly and respect Pinterest's terms of service.**