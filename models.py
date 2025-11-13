from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CarListing(BaseModel):
    """Model for individual car listing"""
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    price: Optional[float] = None
    mileage: Optional[int] = None
    vin: Optional[str] = None
    stock_number: Optional[str] = None
    exterior_color: Optional[str] = None
    interior_color: Optional[str] = None
    transmission: Optional[str] = None
    fuel_type: Optional[str] = None
    engine: Optional[str] = None
    drivetrain: Optional[str] = None
    body_style: Optional[str] = None
    description: Optional[str] = None
    features: List[str] = Field(default_factory=list)
    image_urls: List[str] = Field(default_factory=list)
    listing_url: Optional[str] = None

    # LLM-friendly summary
    def to_llm_summary(self) -> str:
        """Generate a concise summary for LLM consumption"""
        parts = []
        if self.year:
            parts.append(str(self.year))
        if self.make:
            parts.append(self.make)
        if self.model:
            parts.append(self.model)

        summary = " ".join(parts) if parts else "Unknown Vehicle"

        details = []
        if self.price:
            details.append(f"Price: ${self.price:,.2f}")
        if self.mileage:
            details.append(f"Mileage: {self.mileage:,} miles")
        if self.exterior_color:
            details.append(f"Color: {self.exterior_color}")
        if self.transmission:
            details.append(f"Transmission: {self.transmission}")

        if details:
            summary += f" - {', '.join(details)}"

        if self.description:
            summary += f" | Description: {self.description[:200]}"

        return summary


class ScraperResponse(BaseModel):
    """Response model for the scraper API"""
    success: bool
    total_cars: int
    cars: List[CarListing]
    scraped_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    errors: List[str] = Field(default_factory=list)

    # LLM-friendly format
    def to_llm_format(self) -> dict:
        """Format data optimally for LLM consumption"""
        return {
            "summary": f"Found {self.total_cars} vehicles at the dealership",
            "scraped_at": self.scraped_at,
            "vehicles": [
                {
                    "summary": car.to_llm_summary(),
                    "full_details": car.model_dump(exclude_none=True)
                }
                for car in self.cars
            ],
            "errors": self.errors if self.errors else None
        }
