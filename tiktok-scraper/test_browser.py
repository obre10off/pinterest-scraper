#!/usr/bin/env python3
"""
Simple browser test to verify Playwright setup
"""

import asyncio
from loguru import logger
from tiktok_scraper import TikTokScraper


async def test_browser_setup():
    """Test basic browser setup and navigation"""
    scraper = None
    try:
        logger.info("Testing browser setup...")
        scraper = TikTokScraper(headless=False)  # Use visible browser for testing
        
        # Setup browser
        await scraper.setup_browser()
        logger.success("Browser setup successful!")
        
        # Test navigation to a simple page first
        logger.info("Testing navigation...")
        await scraper.page.goto("https://httpbin.org/user-agent", timeout=30000)
        logger.success("Navigation successful!")
        
        # Get the user agent to verify it's working
        user_agent = await scraper.page.evaluate("() => navigator.userAgent")
        logger.info(f"User Agent: {user_agent}")
        
        # Test TikTok navigation (just to the main page first)
        logger.info("Testing TikTok main page...")
        await scraper.page.goto("https://www.tiktok.com", timeout=30000)
        await asyncio.sleep(3)  # Wait for page to load
        
        # Check if page loaded
        title = await scraper.page.title()
        logger.info(f"TikTok page title: {title}")
        
        if "TikTok" in title:
            logger.success("Successfully reached TikTok!")
        else:
            logger.warning("TikTok page may not have loaded properly")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise
    finally:
        if scraper:
            await scraper.cleanup()


if __name__ == "__main__":
    asyncio.run(test_browser_setup())