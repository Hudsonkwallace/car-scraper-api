from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from scraper import CarDealerScraper
from models import ScraperResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Car Dealership Scraper API",
    description="API for scraping car inventory from US Auto Dealers websites",
    version="1.0.0"
)

# Add CORS middleware to allow n8n to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your n8n domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Car Dealership Scraper API",
        "version": "1.0.0",
        "endpoints": {
            "/scrape": "Scrape car inventory from a dealership website",
            "/health": "Health check endpoint"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/scrape", response_model=dict)
async def scrape_inventory(
    url: str = Query(
        default="https://www.usautosofdallas.com/",
        description="The dealership website URL to scrape"
    ),
    llm_format: bool = Query(
        default=True,
        description="Return data in LLM-friendly format"
    ),
    headless: bool = Query(
        default=True,
        description="Run browser in headless mode"
    )
):
    """
    Scrape car inventory from the specified dealership website

    Args:
        url: The dealership website URL (default: https://www.usautosofdallas.com/)
        llm_format: Whether to return data in LLM-friendly format (default: True)
        headless: Whether to run browser in headless mode (default: True)

    Returns:
        JSON response with car inventory data
    """
    try:
        logger.info(f"Received scrape request for: {url}")

        # Initialize scraper
        scraper = CarDealerScraper(headless=headless)

        # Scrape the inventory
        result = scraper.scrape_inventory(url)

        # Return appropriate format
        if llm_format:
            response_data = result.to_llm_format()
        else:
            response_data = result.model_dump()

        logger.info(f"Scraping completed. Found {result.total_cars} vehicles")

        return JSONResponse(content=response_data)

    except Exception as e:
        logger.error(f"Error during scraping: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Scraping failed: {str(e)}"
        )


@app.post("/scrape")
async def scrape_inventory_post(
    url: str = "https://www.usautosofdallas.com/",
    llm_format: bool = True,
    headless: bool = True
):
    """
    POST endpoint for scraping (useful for n8n workflows that prefer POST)

    Args:
        url: The dealership website URL
        llm_format: Whether to return data in LLM-friendly format
        headless: Whether to run browser in headless mode

    Returns:
        JSON response with car inventory data
    """
    return await scrape_inventory(url=url, llm_format=llm_format, headless=headless)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
