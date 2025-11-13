"""
Test the updated scraper locally
"""
import sys
import logging

logging.basicConfig(level=logging.INFO)

from scraper import CarDealerScraper

print("🚗 Testing car scraper...")
print("=" * 50)

scraper = CarDealerScraper(headless=False)  # Set to False to see browser
result = scraper.scrape_inventory("https://www.usautosofdallas.com/")

print("\n" + "=" * 50)
print(f"✅ Success: {result.success}")
print(f"📊 Total Cars Found: {result.total_cars}")
print(f"🕐 Scraped At: {result.scraped_at}")

if result.errors:
    print(f"\n⚠️  Errors ({len(result.errors)}):")
    for error in result.errors[:5]:
        print(f"  - {error}")

if result.cars:
    print("\n" + "=" * 50)
    print(f"Sample Vehicles (first 5 of {len(result.cars)}):")
    print("=" * 50)

    for i, car in enumerate(result.cars[:5], 1):
        print(f"\n🚙 Vehicle #{i}:")
        if car.year or car.make or car.model:
            print(f"  {car.year} {car.make} {car.model}")
        if car.price:
            print(f"  Price: ${car.price:,.2f}")
        if car.mileage:
            print(f"  Mileage: {car.mileage:,} miles")
        if car.listing_url:
            print(f"  URL: {car.listing_url}")
else:
    print("\n❌ No vehicles found!")

print("\n" + "=" * 50)
print("✨ Test complete!")
