# TikTok Slideshow Scraper & Hook Analyzer

A sophisticated TikTok profile scraper designed to collect slideshow/carousel posts and extract hooks for training content generation models.

## Features

- 🎯 **Targeted Scraping**: Scrape specific TikTok profiles you provide
- 🖼️ **Slideshow Focus**: Automatically detects and filters slideshow/carousel posts
- 📝 **Hook Extraction**: Extracts and analyzes opening hooks from captions
- 🧠 **Smart Categorization**: Categorizes hooks by type (question, story, list, etc.)
- 📊 **Training Dataset Generation**: Creates ML-ready datasets for hook training
- 🛡️ **Anti-Detection**: Built-in stealth measures to avoid blocking
- 🎨 **Beautiful CLI**: User-friendly command-line interface with colored output

## Installation

1. Clone or navigate to the tiktok-scraper directory:
```bash
cd tiktok-scraper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browser:
```bash
playwright install chromium
```

4. Verify setup:
```bash
python cli.py setup
```

## Quick Start

### 1. Add Profiles to Track

Add TikTok profiles you want to scrape:
```bash
python cli.py add username1 username2 @username3
```

### 2. List Tracked Profiles

View all profiles and their status:
```bash
python cli.py list
```

### 3. Scrape Profiles

Scrape all pending profiles:
```bash
python cli.py scrape
```

Or scrape specific profiles:
```bash
python cli.py scrape --profiles username1 --profiles username2
```

### 4. Analyze Hooks

Generate training dataset from scraped content:
```bash
python cli.py analyze
```

## CLI Commands

### Profile Management

- `add [usernames...]` - Add profiles to track
- `remove [usernames...]` - Remove profiles from tracking
- `list` - Show all profiles and their status
- `info [username]` - Get detailed info about a profile
- `reset [usernames...]` - Reset profile status to pending

### Scraping Operations

- `scrape` - Scrape TikTok profiles
  - `--profiles/-p` - Specific profiles to scrape
  - `--all` - Scrape all pending profiles
  - `--limit/-l` - Limit posts per profile
  - `--headless` - Run browser in headless mode
  - `--slideshows-only` - Only scrape slideshow posts (default: true)

### Analysis & Training

- `analyze` - Generate training dataset from scraped hooks
  - `--output/-o` - Output file path (default: training_dataset.json)
  - `--data-dir/-d` - Directory with scraped data (default: scraped_data)

### Utilities

- `setup` - Check and setup environment
- `clean` - Clean all scraped data and reset profiles
  - `--force` - Skip confirmation prompt

## Data Structure

```
tiktok-scraper/
├── scraped_data/
│   ├── {username}/
│   │   ├── slideshows.json      # All slideshow posts
│   │   ├── hooks.txt            # Extracted hooks
│   │   └── metadata.json        # Profile metadata
│   └── ...
├── training_dataset.json        # ML training data
├── training_dataset_simplified.json  # Simplified format
├── profiles.json                # Profile tracking
└── config.json                  # Configuration
```

## Hook Categories

The analyzer categorizes hooks into these types:

- **Question**: Starts with interrogative words (how, why, what)
- **Story**: POV, story time, personal narratives
- **List**: Numbered lists, top X, best/worst
- **Challenge**: Dares, challenges, "try this"
- **Emotional**: Strong emotional appeals with urgency
- **Educational**: Learn, tutorial, guide content
- **Controversial**: Hot takes, unpopular opinions
- **Statement**: General declarative hooks

## Configuration

Edit `config.json` to customize:

```json
{
  "scraper_settings": {
    "headless": false,
    "timeout": 30000,
    "scroll_pause_time": 3,
    "max_scrolls": 10,
    "slideshows_only": true
  },
  "rate_limiting": {
    "min_delay": 3,
    "max_delay": 10
  },
  "filters": {
    "min_likes": 1000,
    "min_views": 5000,
    "slideshow_only": true
  }
}
```

## Training Data Format

The generated training dataset includes:

- **Hooks**: Extracted text with categorization
- **Quality Scores**: Engagement and clarity metrics  
- **Patterns**: Common openings, endings, word frequency
- **Statistics**: Average lengths, emoji usage, etc.
- **Metadata**: Post IDs, authors, engagement stats

## Example Workflow

```bash
# 1. Setup environment
python cli.py setup

# 2. Add profiles to scrape
python cli.py add creativeprofile1 trendingcreator2 viralaccount3

# 3. Check profile list
python cli.py list

# 4. Scrape profiles
python cli.py scrape --all

# 5. Generate training dataset
python cli.py analyze --output my_hooks_dataset.json

# 6. View specific profile data
python cli.py info creativeprofile1
```

## Important Notes

- **Rate Limiting**: The scraper includes delays to avoid detection
- **Ethical Use**: Only scrape public profiles and respect TikTok's ToS
- **Browser Window**: By default runs with visible browser (set headless in config)
- **Slideshow Focus**: Optimized for photo slideshows, not video content
- **Data Privacy**: No private user data is collected

## Troubleshooting

### Browser Issues
If Playwright browser isn't working:
```bash
playwright install chromium
playwright install-deps  # On Linux
```

### No Posts Found
- Ensure the profile is public
- Check if the profile has slideshow content
- Try increasing `max_scrolls` in config

### Rate Limiting
If getting blocked:
- Increase delays in config
- Use fewer profiles per session
- Consider using proxies (advanced)

## Advanced Usage

### Custom Scraping
```python
from tiktok_scraper import TikTokScraper
import asyncio

async def custom_scrape():
    scraper = TikTokScraper(headless=True)
    results = await scraper.scrape_multiple_profiles(["username1", "username2"])
    return results

results = asyncio.run(custom_scrape())
```

### Hook Analysis
```python
from hook_analyzer import HookAnalyzer

analyzer = HookAnalyzer()
training_data = analyzer.process_scraped_data("scraped_data")
analyzer.save_training_data(training_data, "custom_dataset.json")
```

## License

This tool is for educational purposes. Please respect TikTok's terms of service and creator content rights.