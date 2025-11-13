"""
Quick local test - simpler than full scraper
Just checks if we can access the site with Selenium
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

print("🚀 Starting quick test...")

# Setup Chrome options
chrome_options = Options()
# chrome_options.add_argument("--headless=new")  # Comment out to see browser
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

print("📦 Installing ChromeDriver...")
try:
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    print("🌐 Navigating to website...")
    driver.get("https://www.usautosofdallas.com/inventory")

    print("⏳ Waiting for page to load...")
    time.sleep(5)

    # Get page info
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    page_title = soup.find('title')
    print(f"\n✅ Page Title: {page_title.get_text() if page_title else 'No title'}")
    print(f"📄 Page Length: {len(page_source)} characters")

    # Find all divs with class
    divs = soup.find_all('div', class_=True)
    print(f"\n🔍 Found {len(divs)} divs with classes")

    # Sample classes
    classes = []
    for div in divs[:50]:
        class_list = div.get('class', [])
        classes.extend(class_list)

    unique_classes = set(classes)
    print(f"📝 Sample classes: {list(unique_classes)[:20]}")

    # Look for vehicle-related content
    vehicle_keywords = ['vehicle', 'car', 'inventory', 'listing', 'price']
    found_keywords = []

    for keyword in vehicle_keywords:
        elements = soup.find_all(class_=lambda x: x and keyword in str(x).lower())
        if elements:
            found_keywords.append(f"{keyword}: {len(elements)} elements")

    print(f"\n🚗 Vehicle-related elements:")
    for item in found_keywords:
        print(f"  - {item}")

    # Print first 1000 chars of HTML
    print(f"\n📋 HTML Snippet (first 1000 chars):")
    print(page_source[:1000])

    driver.quit()
    print("\n✅ Test complete!")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
