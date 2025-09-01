# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Pinterest image URL scraper that bypasses API limitations by using Selenium WebDriver for browser automation. The system implements sophisticated anti-detection measures and extracts **only TikTok/Instagram-optimized images** with perfect aspect ratios and dimensions for social media content creation.

## Core Architecture

### Social Media Optimization Engine

1. **Core Engine** (`enhanced_scraper.py`): `EnhancedPinterestScraper` class with dimension detection and filtering
2. **Entry Points**: Multiple execution modes for different use cases
3. **Output Management**: Aspect-ratio organized file structure with social media metadata

### Key Components

- **`main.py`**: Primary orchestrator with quick/full modes
- **`enhanced_scraper.py`**: Core scraping engine with social media dimension filtering
- **`image_url_scraper.py`**: Lightweight URL-only alternative (inherits social media filtering)
- **`download_images.py`**: Optional image downloading utility
- **`test_setup.py`**: Environment validation tool
- **`test_social_dimensions.py`**: Social media dimension validation suite
- **`test_originals_only.py`**: Updated to test social media optimization

### Critical Filtering Logic

The scraper is configured for **social media optimization**:
```python
# Only accept originals URLs
if 'originals' not in src:
    return None

# Check dimensions for TikTok/Instagram compatibility
dimensions = self.get_image_dimensions(original_src)
is_compatible, aspect_match, quality_score = self.is_social_media_compatible(width, height)
if not is_compatible:
    return None  # Skip non-social-media dimensions
```

### Target Aspect Ratios
- **9:16** - TikTok, Instagram Stories/Reels (1080×1920 optimal)
- **1:1** - Instagram Square Posts (1080×1080 optimal)  
- **4:5** - Instagram Feed Posts (1080×1350 optimal)

## Development Commands

### Setup and Validation
```bash
# Install dependencies (includes Pillow for image analysis)
pip install -r requirements.txt

# Verify setup (checks Chrome, Selenium, permissions)
python test_setup.py

# Test social media dimension filtering
python test_originals_only.py

# Comprehensive social media dimension testing
python test_social_dimensions.py
```

### Scraping Operations
```bash
# Quick scrape (30 images/category, URLs only)
python main.py

# Full scrape (50 images/category, complete metadata)
python main.py --full

# Lightweight URL-only scraper
python image_url_scraper.py

# Direct enhanced scraper usage
python enhanced_scraper.py
```

### Image Download Operations
```bash
# Download all categories (30 images each)
python download_images.py

# Download specific category with limit
python download_images.py entrepreneur 20
```

## Anti-Detection Implementation

### Browser Stealth Configuration
- Disables automation flags (`--disable-blink-features=AutomationControlled`)
- Randomizes window sizes and user agents
- Executes stealth JavaScript to hide webdriver properties
- Uses human-like scrolling patterns with variable delays

### Rate Limiting Strategy
- Random delays between actions (1.5-10 seconds)
- Extended breaks every 10 scrolls (5-10 seconds)
- Category separation pauses (10-20 seconds)
- No new images detection with early exit

## Data Flow Architecture

### Scraping Pipeline
1. **Browser Initialization**: Chrome setup with anti-detection measures
2. **Category Processing**: Sequential category scraping with breaks
3. **Image Discovery**: Scroll-based element detection
4. **URL Filtering**: Strict originals-only filtering
5. **Data Extraction**: Metadata collection (alt text, pin URLs, timestamps)
6. **Output Generation**: Multiple format exports

### Output Structure
```
findings/
├── {category_name}/
│   ├── social_media_urls.txt    # Main summary with dimensions and platform guidance
│   ├── 9x16/                   # TikTok, Instagram Stories/Reels
│   │   └── urls_only.txt
│   ├── 1x1/                    # Instagram Square Posts  
│   │   └── urls_only.txt
│   ├── 4x5/                    # Instagram Feed Posts
│   │   └── urls_only.txt
│   ├── image_data.json         # Full metadata with dimensions
│   └── images/                 # Downloaded files (optional)
└── all_image_urls.json         # Master aggregation
```

## Target Categories
Predefined list of 12 categories: Entrepreneur, Selfie Couples, Laptop Study, NYC Lifestyle, Faceless Selfies, Surrealism, Fall Evening, Summer Lake, School, Burning, Gym, Aesthetic Books.

## Critical Implementation Notes

### Social Media Filtering Logic
- **URL Filter**: Only `https://i.pinimg.com/originals/...` URLs
- **Dimension Check**: Downloads image headers to get exact dimensions
- **Aspect Ratio Filter**: Only accepts 9:16, 1:1, and 4:5 ratios
- **Quality Scoring**: Prioritizes 1080p+ images with perfect aspect ratios
- **Result**: 100% social media ready images with optimal dimensions

### Error Handling Patterns
- Graceful category failure handling with continuation
- Element detection timeouts (15-second default)
- Network failure recovery with delays
- State preservation between categories

### Performance Characteristics
- Runtime: 15-45 minutes (dimension checking adds processing time)
- Memory: Moderate (Chrome browser + image processing overhead)
- Output: Variable based on social media compatible images found
- Success Rate: Continues after individual category failures
- Filtering Rate: ~90-95% rejection rate (only social media optimal dimensions accepted)

## Modification Guidelines

### Adding New Categories
Modify the `categories` list in any main file:
```python
categories = [
    "Your New Category",
    "Another Category",
    # Existing categories...
]
```

### Adjusting Image Limits
Change `images_per_category` parameter:
```python
# In main functions
scraper.scrape_multiple_categories(categories, images_per_category=100)
```

### Enabling Headless Mode
```python
scraper = EnhancedPinterestScraper(headless=True)
```

## Dependencies and Environment
- **Python**: 3.7+ (pyproject.toml specifies >=3.12.7)
- **Chrome Browser**: Required for ChromeDriver
- **Key Packages**: `selenium==4.15.2`, `requests==2.31.0`, `Pillow==10.1.0`
- **Platform**: Cross-platform (Windows, macOS, Linux user agents)
- **New Capability**: Image dimension detection and social media optimization