"""
Quick script to see the actual HTML structure of vehicle listings
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

chrome_options = Options()
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

driver.get("https://www.usautosofdallas.com/inventory")
time.sleep(5)

page_source = driver.page_source
soup = BeautifulSoup(page_source, 'html.parser')

# Save the full HTML for inspection
with open('inventory_page.html', 'w', encoding='utf-8') as f:
    f.write(soup.prettify())

print("✅ Saved full page HTML to inventory_page.html")

# Find ALL divs that contain "vehicle" in any attribute
vehicle_divs = []
for div in soup.find_all('div'):
    div_str = str(div)[:500]  # First 500 chars
    if 'vehicle' in div_str.lower() and len(div_str) > 100:
        classes = div.get('class', [])
        vehicle_divs.append({
            'classes': classes,
            'has_link': bool(div.find('a')),
            'snippet': div_str[:200]
        })

print(f"\n🔍 Found {len(vehicle_divs)} divs with 'vehicle' in them")
print("\nFirst 5 examples:")
for i, vdiv in enumerate(vehicle_divs[:5], 1):
    print(f"\n{i}. Classes: {vdiv['classes']}")
    print(f"   Has link: {vdiv['has_link']}")
    print(f"   Snippet: {vdiv['snippet'][:150]}...")

driver.quit()
print("\n✅ Done! Check inventory_page.html for full source")
