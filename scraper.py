import logging
import re
from typing import List, Optional
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from models import CarListing, ScraperResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CarDealerScraper:
    """Scraper for US Auto Dealers websites"""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None

    def _init_driver(self):
        """Initialize Selenium WebDriver"""
        import os
        import shutil

        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

        # Check if running in Railway/Nixpacks environment
        chrome_bin = shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome")
        chromedriver_path = shutil.which("chromedriver")

        if chrome_bin:
            logger.info(f"Using system Chrome at: {chrome_bin}")
            chrome_options.binary_location = chrome_bin

        if chromedriver_path:
            logger.info(f"Using system ChromeDriver at: {chromedriver_path}")
            service = Service(chromedriver_path)
        else:
            logger.info("Using webdriver-manager to download ChromeDriver")
            service = Service(ChromeDriverManager().install())

        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def _close_driver(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def _extract_number(self, text: str) -> Optional[int]:
        """Extract number from text"""
        if not text:
            return None
        match = re.search(r'\d+', text.replace(',', ''))
        return int(match.group()) if match else None

    def _extract_price(self, text: str) -> Optional[float]:
        """Extract price from text"""
        if not text:
            return None
        match = re.search(r'\$?([\d,]+)', text)
        if match:
            return float(match.group(1).replace(',', ''))
        return None

    def _parse_vehicle_title(self, title: str) -> dict:
        """Parse vehicle title to extract year, make, model"""
        result = {"year": None, "make": None, "model": None}
        if not title:
            return result

        # Common pattern: "YEAR MAKE MODEL" or "YEAR MAKE MODEL TRIM"
        parts = title.strip().split()
        if len(parts) >= 3:
            # First part is often the year
            if parts[0].isdigit() and len(parts[0]) == 4:
                result["year"] = int(parts[0])
                result["make"] = parts[1]
                result["model"] = " ".join(parts[2:])
            else:
                # Try to find year in the string
                for i, part in enumerate(parts):
                    if part.isdigit() and len(part) == 4:
                        result["year"] = int(part)
                        if i > 0:
                            result["make"] = parts[i-1]
                        if i < len(parts) - 1:
                            result["model"] = " ".join(parts[i+1:])
                        break

        return result

    def scrape_inventory(self, url: str = "https://www.usautosofdallas.com/") -> ScraperResponse:
        """
        Scrape the entire inventory from the dealership website

        Args:
            url: The dealership website URL

        Returns:
            ScraperResponse with all car listings
        """
        errors = []
        cars = []

        try:
            logger.info(f"Starting scrape of {url}")
            self._init_driver()

            # Navigate to the inventory page
            inventory_url = url.rstrip('/') + '/inventory'
            logger.info(f"Navigating to {inventory_url}")
            self.driver.get(inventory_url)

            # Wait for page to load
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except Exception as e:
                logger.warning(f"Timeout waiting for page load: {e}")

            # Get page source and parse with BeautifulSoup
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'lxml')

            # Debug: Log page title to verify we got the right page
            page_title = soup.find('title')
            logger.info(f"Page title: {page_title.get_text() if page_title else 'No title found'}")

            # Debug: Save HTML snippet for analysis
            logger.info(f"Page source length: {len(page_source)} characters")

            # Try different common selectors for vehicle listings
            # These are common patterns used by dealership websites
            vehicle_selectors = [
                {'class': 'vehicle-card'},
                {'class': 'inventory-item'},
                {'class': 'car-item'},
                {'class': 'vehicle-listing'},
                {'class': 'vehicle'},
                {'class': 'inventory-vehicle'},
                {'data-type': 'vehicle'},
            ]

            vehicle_elements = []
            for selector in vehicle_selectors:
                elements = soup.find_all('div', selector)
                if elements:
                    logger.info(f"Found {len(elements)} vehicles using selector: {selector}")
                    vehicle_elements = elements
                    break

            # If no specific vehicle cards found, try to find individual vehicle links
            if not vehicle_elements:
                logger.info("No vehicle cards found, looking for vehicle detail links")
                # Look for links that might lead to vehicle details
                links = soup.find_all('a', href=re.compile(r'/(vehicle|inventory|car)/'))
                vehicle_links = list(set([link.get('href') for link in links if link.get('href')]))
                logger.info(f"Found {len(vehicle_links)} potential vehicle links")

                # Scrape each vehicle detail page
                for link in vehicle_links[:50]:  # Limit to first 50 to avoid too long scraping
                    try:
                        car = self._scrape_vehicle_detail(url, link)
                        if car:
                            cars.append(car)
                    except Exception as e:
                        logger.error(f"Error scraping vehicle at {link}: {e}")
                        errors.append(f"Failed to scrape {link}: {str(e)}")

            else:
                # Parse each vehicle card
                for vehicle_elem in vehicle_elements:
                    try:
                        car = self._parse_vehicle_card(vehicle_elem, url)
                        if car:
                            cars.append(car)
                    except Exception as e:
                        logger.error(f"Error parsing vehicle card: {e}")
                        errors.append(f"Failed to parse vehicle: {str(e)}")

            logger.info(f"Successfully scraped {len(cars)} vehicles")

        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            errors.append(f"Scraping error: {str(e)}")

        finally:
            self._close_driver()

        return ScraperResponse(
            success=len(cars) > 0,
            total_cars=len(cars),
            cars=cars,
            errors=errors
        )

    def _parse_vehicle_card(self, element, base_url: str) -> Optional[CarListing]:
        """Parse a vehicle card element"""
        car_data = {}

        # Extract title/name
        title_elem = (element.find('h2') or element.find('h3') or
                     element.find('h4') or element.find(class_=re.compile(r'title|name')))
        if title_elem:
            title = title_elem.get_text(strip=True)
            parsed = self._parse_vehicle_title(title)
            car_data.update(parsed)

        # Extract price
        price_elem = element.find(class_=re.compile(r'price'))
        if price_elem:
            car_data['price'] = self._extract_price(price_elem.get_text(strip=True))

        # Extract mileage
        mileage_elem = element.find(class_=re.compile(r'mileage|miles'))
        if mileage_elem:
            car_data['mileage'] = self._extract_number(mileage_elem.get_text(strip=True))

        # Extract link
        link_elem = element.find('a', href=True)
        if link_elem:
            href = link_elem['href']
            if not href.startswith('http'):
                href = base_url.rstrip('/') + '/' + href.lstrip('/')
            car_data['listing_url'] = href

        # Extract images
        images = []
        for img in element.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if src and not src.endswith(('.svg', '.gif')):
                if not src.startswith('http'):
                    src = base_url.rstrip('/') + '/' + src.lstrip('/')
                images.append(src)
        car_data['image_urls'] = images

        return CarListing(**car_data) if car_data else None

    def _scrape_vehicle_detail(self, base_url: str, path: str) -> Optional[CarListing]:
        """Scrape a single vehicle detail page"""
        try:
            url = path if path.startswith('http') else base_url.rstrip('/') + '/' + path.lstrip('/')
            logger.info(f"Scraping vehicle detail: {url}")

            self.driver.get(url)
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            car_data = {'listing_url': url}

            # Extract title
            title_elem = soup.find('h1') or soup.find('h2')
            if title_elem:
                parsed = self._parse_vehicle_title(title_elem.get_text(strip=True))
                car_data.update(parsed)

            # Extract all text content for additional details
            text_content = soup.get_text()

            # Look for VIN
            vin_match = re.search(r'VIN[:\s]+([A-HJ-NPR-Z0-9]{17})', text_content, re.IGNORECASE)
            if vin_match:
                car_data['vin'] = vin_match.group(1)

            # Look for stock number
            stock_match = re.search(r'Stock[#\s:]+([A-Z0-9-]+)', text_content, re.IGNORECASE)
            if stock_match:
                car_data['stock_number'] = stock_match.group(1)

            # Extract price
            price_elem = soup.find(class_=re.compile(r'price'))
            if price_elem:
                car_data['price'] = self._extract_price(price_elem.get_text(strip=True))

            # Extract mileage
            mileage_match = re.search(r'(\d+,?\d*)\s*miles?', text_content, re.IGNORECASE)
            if mileage_match:
                car_data['mileage'] = self._extract_number(mileage_match.group(1))

            # Extract images
            images = []
            for img in soup.find_all('img'):
                src = img.get('src') or img.get('data-src')
                if src and not src.endswith(('.svg', '.gif')) and 'logo' not in src.lower():
                    if not src.startswith('http'):
                        src = base_url.rstrip('/') + '/' + src.lstrip('/')
                    images.append(src)
            car_data['image_urls'] = images[:10]  # Limit to 10 images

            return CarListing(**car_data)

        except Exception as e:
            logger.error(f"Error scraping detail page {path}: {e}")
            return None
