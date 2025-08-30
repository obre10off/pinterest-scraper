#!/usr/bin/env python3
"""
Test script to check if the scraper setup works
"""

import os

def test_selenium_import():
    try:
        from selenium import webdriver
        print("✅ Selenium imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Selenium import failed: {e}")
        return False

def test_chrome_driver():
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # Try to create driver
        driver = webdriver.Chrome(options=options)
        driver.get("https://www.google.com")
        title = driver.title
        driver.quit()
        
        print("✅ Chrome WebDriver works!")
        print(f"   Test page title: {title}")
        return True
        
    except Exception as e:
        print(f"❌ Chrome WebDriver failed: {e}")
        print("\n💡 Possible solutions:")
        print("   1. Install Chrome browser: https://www.google.com/chrome/")
        print("   2. Or install ChromeDriver: brew install chromedriver")
        print("   3. Or use Firefox instead (install geckodriver)")
        return False

def test_create_folders():
    try:
        test_folder = "findings/test_category"
        os.makedirs(test_folder, exist_ok=True)
        
        # Write a test file
        with open(f"{test_folder}/test.txt", "w") as f:
            f.write("Test file")
        
        print("✅ Folder creation works!")
        print(f"   Created: {test_folder}")
        
        # Clean up
        os.remove(f"{test_folder}/test.txt")
        os.rmdir(test_folder)
        os.rmdir("findings")
        
        return True
        
    except Exception as e:
        print(f"❌ Folder creation failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Pinterest Scraper Setup")
    print("=" * 40)
    
    all_good = True
    
    all_good &= test_selenium_import()
    all_good &= test_chrome_driver()  
    all_good &= test_create_folders()
    
    print("\n" + "=" * 40)
    if all_good:
        print("🎉 All tests passed! You're ready to scrape.")
        print("   Run: python main.py")
    else:
        print("⚠️  Some tests failed. Fix the issues above first.")
        
    print("\n📍 The 'findings' folder will be created here:")
    print(f"   {os.getcwd()}/findings/")