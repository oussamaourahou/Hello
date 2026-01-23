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
    MenuExtractionResult,
    ImageGenerationResult
)
from backend.services.vision_service import VisionService
from backend.services.photoroom_service import (
    PhotoroomService,
    PhotoroomCreditsExhaustedError,
    PhotoroomAPIKeyError,
    PhotoroomAPIError
)
from backend.services.image_generation_service import ImageGenerationService
from backend.services.auth_service import get_current_user

# Optional: Database service (requires Supabase)
try:
    from backend.services.database_service import get_database_service
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("⚠️  Supabase not installed. Database endpoints will not work.")

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
image_generation_service = ImageGenerationService()

# Initialize database service if Supabase is available
if SUPABASE_AVAILABLE:
    db_service = get_database_service()
else:
    db_service = None


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


@app.post("/api/generate-image", response_model=ImageGenerationResult)
async def generate_image(
    dish_name: str = Form(...),
    cuisine_style: str = Form(None),
    user: Dict = Depends(get_current_user)
):
    """
    Generate an AI food photo using DALL-E 3 (Protected)

    Args:
        dish_name: Name of the dish to generate
        cuisine_style: Optional cuisine style (e.g., "Moroccan", "French", "Nordic")
        user: Authenticated user (injected by Clerk)

    Returns:
        ImageGenerationResult with generated image URL and details
    """
    try:
        result = await image_generation_service.generate_food_image(
            dish_name=dish_name,
            cuisine_style=cuisine_style
        )

        return ImageGenerationResult(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating image: {str(e)}")


# ==================== NEW: 5-SCREEN FLOW ENDPOINTS ====================

def check_database_available():
    """Check if database service is available"""
    if not SUPABASE_AVAILABLE or db_service is None:
        raise HTTPException(
            status_code=503,
            detail="Database not configured. Please set up Supabase to use restaurant workflow features."
        )

@app.post("/api/restaurants")
async def create_restaurant(
    name: str = Form(...),
    cuisine_type: str = Form(None),
    user: Dict = Depends(get_current_user)
):
    """
    Screen 1: Create a new restaurant (Protected)

    Args:
        name: Restaurant name
        cuisine_type: Type of cuisine (optional)
        user: Authenticated user (injected by Clerk)

    Returns:
        Created restaurant data
    """
    check_database_available()
    try:
        restaurant = await db_service.create_restaurant(
            owner_user_id=user["sub"],
            name=name,
            cuisine_type=cuisine_type
        )
        return restaurant
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating restaurant: {str(e)}")


@app.get("/api/restaurants")
async def get_restaurants(user: Dict = Depends(get_current_user)):
    """
    Screen 1: Get all user's restaurants (Protected)

    Args:
        user: Authenticated user (injected by Clerk)

    Returns:
        List of user's restaurants
    """
    check_database_available()
    try:
        restaurants = await db_service.get_user_restaurants(user["sub"])
        return restaurants
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching restaurants: {str(e)}")


@app.get("/api/restaurants/{restaurant_id}")
async def get_restaurant(
    restaurant_id: str,
    user: Dict = Depends(get_current_user)
):
    """
    Get a specific restaurant (Protected)

    Args:
        restaurant_id: Restaurant UUID
        user: Authenticated user (injected by Clerk)

    Returns:
        Restaurant data
    """
    check_database_available()
    try:
        restaurant = await db_service.get_restaurant(restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")

        # Verify ownership
        if restaurant["owner_user_id"] != user["sub"]:
            raise HTTPException(status_code=403, detail="Access denied")

        return restaurant
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching restaurant: {str(e)}")


@app.post("/api/restaurants/{restaurant_id}/upload-menu")
async def upload_restaurant_menu(
    restaurant_id: str,
    menu_file: UploadFile = File(...),
    user: Dict = Depends(get_current_user)
):
    """
    Screen 2: Upload menu and extract items (Protected)

    Args:
        restaurant_id: Restaurant UUID
        menu_file: Menu PDF or image
        user: Authenticated user (injected by Clerk)

    Returns:
        Extracted menu items
    """
    check_database_available()
    try:
        # Verify restaurant ownership
        restaurant = await db_service.get_restaurant(restaurant_id)
        if not restaurant or restaurant["owner_user_id"] != user["sub"]:
            raise HTTPException(status_code=403, detail="Access denied")

        # Extract menu items (reuse existing logic)
        filename = menu_file.filename.lower()
        is_pdf = filename.endswith('.pdf')
        is_image = filename.endswith(('.jpg', '.jpeg', '.png', '.webp'))

        if not (is_pdf or is_image):
            raise HTTPException(status_code=400, detail="File must be a PDF or image")

        # Save temporary file
        file_path = os.path.join(UPLOAD_DIR, f"menu_{menu_file.filename}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(menu_file.file, buffer)

        # Extract menu items
        extraction_result = await vision_service.extract_menu_items(file_path, is_pdf=is_pdf)

        # Clean up temp file
        if os.path.exists(file_path):
            os.remove(file_path)

        # Save menu items to database
        menu_items = await db_service.create_menu_items(
            restaurant_id=restaurant_id,
            items=extraction_result.menu_items
        )

        # Update restaurant status
        await db_service.update_restaurant_status(restaurant_id, "processing")

        return {
            "extraction_result": extraction_result.dict(),
            "menu_items": menu_items
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading menu: {str(e)}")


@app.post("/api/restaurants/{restaurant_id}/upload-photo")
async def upload_restaurant_photo(
    restaurant_id: str,
    photo: UploadFile = File(...),
    user: Dict = Depends(get_current_user)
):
    """
    Screen 2: Upload a food photo (Protected)

    Args:
        restaurant_id: Restaurant UUID
        photo: Food photo
        user: Authenticated user (injected by Clerk)

    Returns:
        Uploaded photo data
    """
    check_database_available()
    try:
        # Verify restaurant ownership
        restaurant = await db_service.get_restaurant(restaurant_id)
        if not restaurant or restaurant["owner_user_id"] != user["sub"]:
            raise HTTPException(status_code=403, detail="Access denied")

        # Save temporary file
        temp_path = os.path.join(UPLOAD_DIR, photo.filename)
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)

        # Upload to Supabase Storage
        storage_url = await db_service.upload_photo_to_storage(
            file_path=temp_path,
            restaurant_id=restaurant_id,
            file_type="original"
        )

        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

        # Create photo record
        photo_record = await db_service.create_photo(
            restaurant_id=restaurant_id,
            filename=photo.filename,
            storage_path=storage_url,
            source="uploaded"
        )

        return photo_record

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading photo: {str(e)}")


@app.get("/api/restaurants/{restaurant_id}/menu-items")
async def get_restaurant_menu_items(
    restaurant_id: str,
    user: Dict = Depends(get_current_user)
):
    """
    Screen 3: Get all menu items for a restaurant (Protected)

    Args:
        restaurant_id: Restaurant UUID
        user: Authenticated user (injected by Clerk)

    Returns:
        List of menu items
    """
    check_database_available()
    try:
        # Verify restaurant ownership
        restaurant = await db_service.get_restaurant(restaurant_id)
        if not restaurant or restaurant["owner_user_id"] != user["sub"]:
            raise HTTPException(status_code=403, detail="Access denied")

        menu_items = await db_service.get_menu_items(restaurant_id)
        return menu_items

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching menu items: {str(e)}")


@app.get("/api/restaurants/{restaurant_id}/photos")
async def get_restaurant_photos(
    restaurant_id: str,
    user: Dict = Depends(get_current_user)
):
    """
    Screen 3: Get all photos for a restaurant (Protected)

    Args:
        restaurant_id: Restaurant UUID
        user: Authenticated user (injected by Clerk)

    Returns:
        List of photos
    """
    check_database_available()
    try:
        # Verify restaurant ownership
        restaurant = await db_service.get_restaurant(restaurant_id)
        if not restaurant or restaurant["owner_user_id"] != user["sub"]:
            raise HTTPException(status_code=403, detail="Access denied")

        photos = await db_service.get_restaurant_photos(restaurant_id)
        return photos

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching photos: {str(e)}")


@app.post("/api/restaurants/{restaurant_id}/match-all")
async def match_all_photos(
    restaurant_id: str,
    user: Dict = Depends(get_current_user)
):
    """
    Screen 3: Auto-match all photos to menu items (Protected)

    Args:
        restaurant_id: Restaurant UUID
        user: Authenticated user (injected by Clerk)

    Returns:
        Matching results for all photos
    """
    check_database_available()
    try:
        # Verify restaurant ownership
        restaurant = await db_service.get_restaurant(restaurant_id)
        if not restaurant or restaurant["owner_user_id"] != user["sub"]:
            raise HTTPException(status_code=403, detail="Access denied")

        # Get all menu items and photos
        menu_items = await db_service.get_menu_items(restaurant_id)
        photos = await db_service.get_restaurant_photos(restaurant_id)

        if not menu_items:
            raise HTTPException(status_code=400, detail="No menu items found")
        if not photos:
            raise HTTPException(status_code=400, detail="No photos found")

        menu_item_names = [item["name"] for item in menu_items]
        results = []

        # Match each photo
        for photo in photos:
            # Download photo from Supabase Storage temporarily
            import httpx
            temp_path = os.path.join(UPLOAD_DIR, f"temp_{photo['id']}.jpg")

            async with httpx.AsyncClient() as client:
                response = await client.get(photo["storage_path"])
                with open(temp_path, "wb") as f:
                    f.write(response.content)

            # Match photo to menu
            match_result = await vision_service.match_photo_to_menu(temp_path, menu_item_names)

            # Find the matched menu item
            matched_item = next(
                (item for item in menu_items if item["name"] == match_result.matched_item),
                None
            )

            if matched_item:
                # Update menu item with match
                await db_service.update_menu_item_match(
                    menu_item_id=matched_item["id"],
                    matched_photo_id=photo["id"],
                    confidence=match_result.confidence,
                    reasoning=match_result.reasoning,
                    photo_source="uploaded"
                )

            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)

            results.append({
                "photo_id": photo["id"],
                "matched_item": match_result.matched_item,
                "confidence": match_result.confidence
            })

        return results

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error matching photos: {str(e)}")


@app.post("/api/restaurants/{restaurant_id}/enhance-all")
async def enhance_all_photos(
    restaurant_id: str,
    user: Dict = Depends(get_current_user)
):
    """
    Screen 4: Enhance all matched photos (Protected)

    Args:
        restaurant_id: Restaurant UUID
        user: Authenticated user (injected by Clerk)

    Returns:
        Enhancement results
    """
    check_database_available()
    try:
        # Verify restaurant ownership
        restaurant = await db_service.get_restaurant(restaurant_id)
        if not restaurant or restaurant["owner_user_id"] != user["sub"]:
            raise HTTPException(status_code=403, detail="Access denied")

        # Get all menu items with matched photos
        menu_items = await db_service.get_menu_items(restaurant_id)
        results = []

        for item in menu_items:
            if not item["matched_photo_id"]:
                continue

            # Get photo
            photo = await db_service.get_photo(item["matched_photo_id"])
            if not photo:
                continue

            # Download photo temporarily
            import httpx
            temp_path = os.path.join(UPLOAD_DIR, f"temp_{photo['id']}.jpg")

            async with httpx.AsyncClient() as client:
                response = await client.get(photo["storage_path"])
                with open(temp_path, "wb") as f:
                    f.write(response.content)

            # Assess quality
            quality_result = await vision_service.assess_photo_quality(temp_path)

            # Save quality assessment
            await db_service.update_menu_item_quality(
                menu_item_id=item["id"],
                quality_score=quality_result.overall_score,
                quality_details=quality_result.dict()
            )

            # Enhance if quality is acceptable
            enhanced_url = None
            if quality_result.overall_quality != "Reject":
                try:
                    # Enhance with Photoroom
                    enhancement_result = await photoroom_service.enhance_photo(temp_path, "white")

                    # Upload enhanced photo to Supabase Storage
                    enhanced_url = await db_service.upload_photo_to_storage(
                        file_path=enhancement_result.enhanced_image_url,
                        restaurant_id=restaurant_id,
                        file_type="enhanced"
                    )

                    # Update menu item with enhanced URL
                    await db_service.update_menu_item_enhanced_photo(
                        menu_item_id=item["id"],
                        enhanced_photo_url=enhanced_url
                    )
                except Exception as e:
                    # Non-fatal error, continue with other photos
                    pass

            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)

            results.append({
                "menu_item_id": item["id"],
                "menu_item_name": item["name"],
                "quality_score": quality_result.overall_score,
                "enhanced_url": enhanced_url
            })

        # Update restaurant status to ready
        await db_service.update_restaurant_status(restaurant_id, "ready")

        return results

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error enhancing photos: {str(e)}")


@app.get("/api/restaurants/{restaurant_id}/export")
async def export_restaurant_data(
    restaurant_id: str,
    user: Dict = Depends(get_current_user)
):
    """
    Screen 5: Export complete restaurant data (Protected)

    Args:
        restaurant_id: Restaurant UUID
        user: Authenticated user (injected by Clerk)

    Returns:
        Complete restaurant data with menu items and photos
    """
    check_database_available()
    try:
        # Verify restaurant ownership
        restaurant = await db_service.get_restaurant(restaurant_id)
        if not restaurant or restaurant["owner_user_id"] != user["sub"]:
            raise HTTPException(status_code=403, detail="Access denied")

        # Get export data
        export_data = await db_service.get_restaurant_export_data(restaurant_id)

        # Update restaurant status to exported
        await db_service.update_restaurant_status(restaurant_id, "exported")

        return export_data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting data: {str(e)}")


# Mount static files for frontend (must be after all API routes)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
