from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
import shutil
from typing import List
from dotenv import load_dotenv
import json

from backend.models.schemas import (
    PhotoMatchResult,
    PhotoQualityAssessment,
    PhotoroomEnhancementResult
)
from backend.services.vision_service import VisionService
from backend.services.photoroom_service import PhotoroomService

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Glovo Menu AI Pipeline", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize services
vision_service = VisionService()
photoroom_service = PhotoroomService()


@app.get("/api")
async def root():
    return {
        "message": "Glovo Menu AI Pipeline",
        "version": "1.0.0",
        "stages": {
            "stage_2": "Photo-to-Item Matching",
            "stage_3": "Quality Assessment",
            "stage_4": "Photo Enhancement (Photoroom)"
        }
    }


@app.post("/api/stage2/match", response_model=PhotoMatchResult)
async def match_photo_to_menu(
    photo: UploadFile = File(...),
    menu_items: str = Form(...)
):
    """
    Stage 2: Match uploaded photo to menu items

    Args:
        photo: Uploaded food photo
        menu_items: JSON array of menu item names

    Returns:
        PhotoMatchResult with matched item and confidence
    """
    try:
        # Parse menu items
        items = json.loads(menu_items)

        if not items:
            raise HTTPException(status_code=400, detail="Menu items list cannot be empty")

        # Save uploaded file
        file_path = os.path.join(UPLOAD_DIR, photo.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)

        # Call vision service
        result = await vision_service.match_photo_to_menu(file_path, items)

        return result

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid menu_items JSON format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing photo: {str(e)}")


@app.post("/api/stage3/assess", response_model=PhotoQualityAssessment)
async def assess_photo_quality(
    photo: UploadFile = File(...)
):
    """
    Stage 3: Assess photo quality

    Args:
        photo: Uploaded food photo

    Returns:
        PhotoQualityAssessment with quality scores
    """
    try:
        # Save uploaded file
        file_path = os.path.join(UPLOAD_DIR, photo.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)

        # Call vision service
        result = await vision_service.assess_photo_quality(file_path)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error assessing photo: {str(e)}")


@app.post("/api/stage4/enhance", response_model=PhotoroomEnhancementResult)
async def enhance_photo(
    photo: UploadFile = File(...),
    background_color: str = Form("white")
):
    """
    Stage 4: Enhance photo using Photoroom API

    Args:
        photo: Uploaded food photo
        background_color: Background color (default: white)

    Returns:
        PhotoroomEnhancementResult with enhanced image path
    """
    try:
        # Save uploaded file
        file_path = os.path.join(UPLOAD_DIR, photo.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)

        # Call Photoroom service
        result = await photoroom_service.enhance_photo(file_path, background_color)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error enhancing photo: {str(e)}")


@app.post("/api/full-pipeline")
async def full_pipeline(
    photo: UploadFile = File(...),
    menu_items: str = Form(...)
):
    """
    Run the full pipeline: Stage 2 -> Stage 3 -> Stage 4

    Args:
        photo: Uploaded food photo
        menu_items: JSON array of menu item names

    Returns:
        Combined results from all stages
    """
    try:
        # Parse menu items
        items = json.loads(menu_items)

        if not items:
            raise HTTPException(status_code=400, detail="Menu items list cannot be empty")

        # Save uploaded file
        file_path = os.path.join(UPLOAD_DIR, photo.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)

        # Stage 2: Match
        match_result = await vision_service.match_photo_to_menu(file_path, items)

        # Stage 3: Quality Assessment
        quality_result = await vision_service.assess_photo_quality(file_path)

        # Stage 4: Enhancement (only if quality is not "Reject")
        enhancement_result = None
        if quality_result.overall_quality != "Reject":
            enhancement_result = await photoroom_service.enhance_photo(file_path, "white")

        return {
            "stage2_match": match_result.dict(),
            "stage3_quality": quality_result.dict(),
            "stage4_enhancement": enhancement_result.dict() if enhancement_result else None
        }

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid menu_items JSON format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in pipeline: {str(e)}")


@app.get("/api/uploads/{filename}")
async def get_upload(filename: str):
    """Serve uploaded/processed images"""
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)


# Mount static files for frontend (must be after all API routes)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
