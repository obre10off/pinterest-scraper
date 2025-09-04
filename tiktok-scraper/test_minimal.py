#!/usr/bin/env python3
"""
Minimal Playwright test to isolate the issue
"""

import asyncio
from playwright.async_api import async_playwright


async def minimal_test():
    """Minimal test of Playwright functionality"""
    print("Testing minimal Playwright setup...")
    
    playwright = None
    browser = None
    
    try:
        # Start Playwright
        print("1. Starting Playwright...")
        playwright = await async_playwright().start()
        print("✓ Playwright started")
        
        # Launch browser
        print("2. Launching browser...")
        browser = await playwright.chromium.launch(headless=False)
        print("✓ Browser launched")
        
        # Create context
        print("3. Creating context...")
        context = await browser.new_context()
        print("✓ Context created")
        
        # Create page
        print("4. Creating page...")
        page = await context.new_page()
        print("✓ Page created")
        
        # Navigate to simple page
        print("5. Testing navigation...")
        await page.goto("https://httpbin.org/get", timeout=15000)
        print("✓ Navigation successful")
        
        # Get title
        title = await page.title()
        print(f"✓ Page title: {title}")
        
        # Close resources
        await page.close()
        await context.close()
        
        print("✓ Test completed successfully!")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        raise
    finally:
        if browser:
            await browser.close()
        if playwright:
            await playwright.stop()


if __name__ == "__main__":
    asyncio.run(minimal_test())