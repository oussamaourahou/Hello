from pydantic import BaseModel, Field
from typing import List, Optional


class MenuItem(BaseModel):
    """Represents a menu item"""
    name: str
    category: Optional[str] = None
    description: Optional[str] = None


class PhotoMatchRequest(BaseModel):
    """Request for photo-to-item matching"""
    menu_items: List[str]  # Simple list of item names


class PhotoMatchResult(BaseModel):
    """Result of photo-to-item matching"""
    matched_item: str
    confidence: int = Field(..., ge=0, le=100)
    description: str
    dish_identified: str  # What the AI sees in the image
    reasoning: str  # Why this match was chosen


class PhotoQualityAssessment(BaseModel):
    """Quality assessment of a photo"""
    resolution_score: int = Field(..., ge=0, le=100)
    lighting_score: int = Field(..., ge=0, le=100)
    composition_score: int = Field(..., ge=0, le=100)
    presentation_score: int = Field(..., ge=0, le=100)
    overall_quality: str  # "Ready" / "Needs Enhancement" / "Reject"
    overall_score: int = Field(..., ge=0, le=100)
    recommendation: str


class PhotoroomEnhancementResult(BaseModel):
    """Result of Photoroom enhancement"""
    enhanced_image_url: str
    original_image_url: str
    transformations_applied: List[str]


class MenuExtractionResult(BaseModel):
    """Result of menu extraction from PDF/image"""
    menu_items: List[str]
    total_items: int
    extraction_notes: str  # Any notes about the extraction


class ImageGenerationResult(BaseModel):
    """Result of AI image generation"""
    image_url: str
    prompt_used: str
    dish_name: str
    generation_model: str
