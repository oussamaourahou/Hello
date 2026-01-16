from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
import shutil
from typing import List, Dict
from dotenv import load_dotenv
import json

from backend.models.schemas import (
    PhotoMatchResult,
    PhotoQualityAssessment,
    PhotoroomEnhancementResult,
    MenuExtractionResult
)
from backend.services.vision_service import VisionService
from backend.services.photoroom_service import (
    PhotoroomService,
    PhotoroomCreditsExhaustedError,
    PhotoroomAPIKeyError,
    PhotoroomAPIError
)
from backend.services.auth_service import get_current_user

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
            "stage_1": "Menu Extraction (PDF/Image)",
            "stage_2": "Photo-to-Item Matching",
            "stage_3": "Quality Assessment",
            "stage_4": "Photo Enhancement (Photoroom)"
        }
    }


@app.post("/api/stage1/extract", response_model=MenuExtractionResult)
async def extract_menu(
    menu_file: UploadFile = File(...),
    user: Dict = Depends(get_current_user)
):
    """
    Stage 1: Extract menu items from uploaded PDF or image (Protected)

    Args:
        menu_file: Uploaded menu file (PDF or image)
        user: Authenticated user (injected by Clerk)

    Returns:
        MenuExtractionResult with extracted menu items
    """
    try:
        # Check file type
        filename = menu_file.filename.lower()
        is_pdf = filename.endswith('.pdf')
        is_image = filename.endswith(('.jpg', '.jpeg', '.png', '.webp'))

        if not (is_pdf or is_image):
            raise HTTPException(
                status_code=400,
                detail="File must be a PDF or image (JPG, PNG, WEBP)"
            )

        # Save uploaded file
        file_extension = filename.split('.')[-1]
        file_path = os.path.join(UPLOAD_DIR, f"menu_{menu_file.filename}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(menu_file.file, buffer)

        # Call vision service to extract menu items
        result = await vision_service.extract_menu_items(file_path, is_pdf=is_pdf)

        # Clean up uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting menu: {str(e)}")


@app.post("/api/stage2/match", response_model=PhotoMatchResult)
async def match_photo_to_menu(
    photo: UploadFile = File(...),
    menu_items: str = Form(...),
    user: Dict = Depends(get_current_user)
):
    """
    Stage 2: Match uploaded photo to menu items (Protected)

    Args:
        photo: Uploaded food photo
        menu_items: JSON array of menu item names
        user: Authenticated user (injected by Clerk)

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
    photo: UploadFile = File(...),
    user: Dict = Depends(get_current_user)
):
    """
    Stage 3: Assess photo quality (Protected)

    Args:
        photo: Uploaded food photo
        user: Authenticated user (injected by Clerk)

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
    background_color: str = Form("white"),
    user: Dict = Depends(get_current_user)
):
    """
    Stage 4: Enhance photo using Photoroom API (Protected)

    Args:
        photo: Uploaded food photo
        background_color: Background color (default: white)
        user: Authenticated user (injected by Clerk)

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

    except PhotoroomCreditsExhaustedError:
        raise HTTPException(
            status_code=402,
            detail="Photoroom credits exhausted. Please top up at https://app.photoroom.com/api-dashboard"
        )
    except PhotoroomAPIKeyError as e:
        raise HTTPException(
            status_code=401,
            detail=str(e)
        )
    except PhotoroomAPIError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error enhancing photo: {str(e)}")


@app.post("/api/full-pipeline")
async def full_pipeline(
    photo: UploadFile = File(...),
    menu_items: str = Form(...),
    user: Dict = Depends(get_current_user)
):
    """
    Run the full pipeline: Stage 2 -> Stage 3 -> Stage 4 (Protected)

    Args:
        photo: Uploaded food photo
        menu_items: JSON array of menu item names
        user: Authenticated user (injected by Clerk)

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
        enhancement_error = None

        if quality_result.overall_quality != "Reject":
            try:
                enhancement_result = await photoroom_service.enhance_photo(file_path, "white")
            except PhotoroomCreditsExhaustedError:
                # Don't fail the whole pipeline, just note the error
                enhancement_error = "Photoroom credits exhausted. Please top up at https://app.photoroom.com/api-dashboard"
            except PhotoroomAPIKeyError as e:
                enhancement_error = str(e)
            except PhotoroomAPIError as e:
                enhancement_error = str(e)

        return {
            "stage2_match": match_result.dict(),
            "stage3_quality": quality_result.dict(),
            "stage4_enhancement": enhancement_result.dict() if enhancement_result else None,
            "stage4_error": enhancement_error
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


@app.get("/api/download/{filename}")
async def download_image(filename: str, dish_name: str = "enhanced_dish"):
    """
    Download enhanced image with custom filename

    Args:
        filename: Image filename in uploads directory
        dish_name: Name of the dish (used as download filename)

    Returns:
        File download with dish name
    """
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    # Sanitize dish name for filename
    safe_dish_name = "".join(c for c in dish_name if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_dish_name = safe_dish_name.replace(' ', '_')

    # Get file extension
    ext = filename.split('.')[-1] if '.' in filename else 'jpg'
    download_filename = f"{safe_dish_name}.{ext}"

    return FileResponse(
        file_path,
        media_type="image/jpeg",
        filename=download_filename,
        headers={"Content-Disposition": f'attachment; filename="{download_filename}"'}
    )


# Mount static files for frontend (must be after all API routes)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
