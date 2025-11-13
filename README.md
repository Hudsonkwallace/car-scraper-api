# Car Dealership Scraper API

A FastAPI-based web scraping service that extracts car inventory data from dealership websites and returns it in an LLM-friendly format for use in n8n workflows.

## Features

- 🚗 Scrapes complete car inventory from dealership websites
- 🤖 Returns data in LLM-optimized format
- 🔄 Supports both GET and POST endpoints for n8n integration
- 🛡️ Handles anti-bot protection with Selenium
- 📊 Structured data with Pydantic models
- 🌐 CORS enabled for cross-origin requests

## Installation

1. Install Python 3.8 or higher

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Chrome/Chromium will be automatically downloaded by webdriver-manager

## Usage

### Running Locally

Start the FastAPI server:
```bash
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### API Endpoints

#### GET /scrape

Scrape car inventory from a dealership website.

**Query Parameters:**
- `url` (optional): The dealership URL to scrape (default: https://www.usautosofdallas.com/)
- `llm_format` (optional): Return LLM-friendly format (default: true)
- `headless` (optional): Run browser in headless mode (default: true)

**Example:**
```bash
curl "http://localhost:8000/scrape?url=https://www.usautosofdallas.com/&llm_format=true"
```

#### POST /scrape

Same functionality as GET endpoint but accepts POST requests (useful for n8n).

### Response Format

#### LLM Format (default)
```json
{
  "summary": "Found 45 vehicles at the dealership",
  "scraped_at": "2025-11-12T10:30:00",
  "vehicles": [
    {
      "summary": "2020 Toyota Camry - Price: $18,500.00, Mileage: 45,000 miles, Color: Black",
      "full_details": {
        "make": "Toyota",
        "model": "Camry",
        "year": 2020,
        "price": 18500.0,
        "mileage": 45000,
        "exterior_color": "Black",
        "vin": "1234567890ABCDEFG",
        "listing_url": "https://...",
        "image_urls": ["https://..."]
      }
    }
  ]
}
```

#### Standard Format (llm_format=false)
```json
{
  "success": true,
  "total_cars": 45,
  "cars": [
    {
      "make": "Toyota",
      "model": "Camry",
      "year": 2020,
      "price": 18500.0,
      "mileage": 45000,
      "vin": "1234567890ABCDEFG",
      "exterior_color": "Black",
      "listing_url": "https://...",
      "image_urls": ["https://..."]
    }
  ],
  "scraped_at": "2025-11-12T10:30:00",
  "errors": []
}
```

## Using with n8n

### Setup in n8n

1. Add an **HTTP Request** node to your workflow

2. Configure the node:
   - **Method**: GET or POST
   - **URL**: `http://your-api-url:8000/scrape`
   - **Query Parameters** (for GET):
     - `url`: The dealership website URL
     - `llm_format`: `true`

3. Add a subsequent node to process the JSON response (e.g., AI node for Claude)

### Example n8n Workflow

```
[Manual Trigger] → [HTTP Request: Scrape] → [Claude AI: Analyze Cars] → [Email Results]
```

## Deployment Options

### Option 1: Local with ngrok (Testing)
```bash
# Start the API
python main.py

# In another terminal, expose with ngrok
ngrok http 8000
```

### Option 2: Railway (Free Tier)
1. Push code to GitHub
2. Connect Railway to your repo
3. Railway will auto-detect Python and deploy
4. Use the Railway URL in n8n

### Option 3: Render (Free Tier)
1. Push code to GitHub
2. Create new Web Service on Render
3. Configure build command: `pip install -r requirements.txt`
4. Configure start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Option 4: Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Development

### Testing the Scraper
```python
from scraper import CarDealerScraper

scraper = CarDealerScraper(headless=False)  # Set False to see browser
result = scraper.scrape_inventory("https://www.usautosofdallas.com/")
print(f"Found {result.total_cars} cars")
```

### API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Troubleshooting

### Chrome Driver Issues
If you get ChromeDriver errors:
```bash
pip install --upgrade webdriver-manager
```

### Headless Mode Issues
If scraping fails in headless mode, try:
```bash
curl "http://localhost:8000/scrape?headless=false"
```

### Website Changes
If the scraper stops working, the website structure may have changed. Update the selectors in [scraper.py](scraper.py).

## License

MIT
