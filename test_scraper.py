"""
Test script for the car scraper
Run this to test the scraper without starting the full API
"""
import json
from scraper import CarDealerScraper

def test_scraper():
    """Test the scraper functionality"""
    print("🚗 Testing Car Dealership Scraper...")
    print("-" * 50)

    # Initialize scraper (set headless=False to see the browser)
    scraper = CarDealerScraper(headless=True)

    # Scrape the inventory
    url = "https://www.usautosofdallas.com/"
    print(f"Scraping: {url}")
    result = scraper.scrape_inventory(url)

    # Print results
    print("\n" + "=" * 50)
    print(f"✅ Success: {result.success}")
    print(f"📊 Total Cars Found: {result.total_cars}")
    print(f"🕐 Scraped At: {result.scraped_at}")

    if result.errors:
        print(f"\n⚠️  Errors: {len(result.errors)}")
        for error in result.errors[:5]:  # Show first 5 errors
            print(f"  - {error}")

    if result.cars:
        print("\n" + "=" * 50)
        print("Sample Vehicles (first 3):")
        print("=" * 50)

        for i, car in enumerate(result.cars[:3], 1):
            print(f"\n🚙 Vehicle #{i}:")
            print(f"  Summary: {car.to_llm_summary()}")
            print(f"  URL: {car.listing_url}")
            if car.image_urls:
                print(f"  Images: {len(car.image_urls)} found")

    # Save full results to JSON
    output_file = "scraper_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result.model_dump(), f, indent=2)
    print(f"\n💾 Full results saved to: {output_file}")

    # Save LLM format
    llm_output_file = "scraper_results_llm.json"
    with open(llm_output_file, 'w', encoding='utf-8') as f:
        json.dump(result.to_llm_format(), f, indent=2)
    print(f"💾 LLM format saved to: {llm_output_file}")

    print("\n" + "=" * 50)
    print("✨ Test complete!")


if __name__ == "__main__":
    test_scraper()
