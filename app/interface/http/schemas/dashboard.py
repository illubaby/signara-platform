"""Pydantic schemas for dashboard endpoints.

HTTP request/response models for dashboard navigation.
"""
from pydantic import BaseModel, Field
from typing import List


class PageSchema(BaseModel):
    """API representation of a navigable page."""
    page_id: str = Field(..., description="URL-safe page identifier")
    title: str = Field(..., description="Human-readable page title")
    
    class Config:
        json_schema_extra = {
            "example": {
                "page_id": "timing-saf",
                "title": "Timing SAF"
            }
        }


class NavigationMenuSchema(BaseModel):
    """API representation of the navigation menu."""
    pages: List[PageSchema] = Field(..., description="List of available pages")
    
    class Config:
        json_schema_extra = {
            "example": {
                "pages": [
                    {"page_id": "timing-saf", "title": "Timing SAF"},
                    {"page_id": "timing-qa", "title": "Timing QA"}
                ]
            }
        }
