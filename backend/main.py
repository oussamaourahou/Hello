from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
import shutil
from typing import List, Optional
from dotenv import load_dotenv
import json

from backend.models.schemas import (
    PhotoMatchResult,
    PhotoQualityAssessment,
    PhotoroomEnhancementResult
)
from backend.services.vision_service import VisionService
from backend.services.photoroom_service import PhotoroomService
from backend.services.email_indexer import EmailIndexer
from backend.services.email_query import EmailQueryService
from backend.services.email_analytics import EmailAnalyticsService
from backend.config import DB_PATH, CORS_ORIGINS, ensure_data_dir

# Load environment variables
load_dotenv()

# Ensure data directory exists
ensure_data_dir()

# Initialize FastAPI app
app = FastAPI(title="Email Archive Explorer", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
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

# Email archive services (use configured DB path)
email_indexer = EmailIndexer(db_path=DB_PATH)
email_query = EmailQueryService(db_path=DB_PATH)
email_analytics = EmailAnalyticsService(db_path=DB_PATH)

# Track indexing status
indexing_status = {"status": "not_started", "progress": None}


@app.on_event("startup")
async def startup_event():
    """Initialize database connections on startup"""
    await email_indexer.connect()
    await email_query.connect()
    await email_analytics.connect()


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connections on shutdown"""
    await email_indexer.close()
    await email_query.close()
    await email_analytics.close()


@app.get("/")
async def root():
    return {
        "message": "Email Archive Explorer",
        "version": "2.0.0",
        "features": {
            "email_archive": "Query and analyze email archives (mbox format)",
            "menu_ai": "Photo-to-menu matching pipeline"
        },
        "db_path": DB_PATH
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


# ============================================
# EMAIL ARCHIVE ENDPOINTS
# ============================================

async def index_mbox_background(mbox_path: str):
    """Background task to index mbox file"""
    global indexing_status
    try:
        indexing_status["status"] = "indexing"
        result = await email_indexer.index_mbox(mbox_path)
        indexing_status["status"] = "completed"
        indexing_status["progress"] = result
    except Exception as e:
        indexing_status["status"] = "error"
        indexing_status["progress"] = {"error": str(e)}


@app.post("/api/email/index")
async def start_indexing(
    background_tasks: BackgroundTasks,
    mbox_path: str = Form(...)
):
    """
    Start indexing an mbox file

    Args:
        mbox_path: Absolute path to the mbox file

    Returns:
        Status message
    """
    global indexing_status

    if indexing_status["status"] == "indexing":
        raise HTTPException(status_code=400, detail="Indexing already in progress")

    if not os.path.exists(mbox_path):
        raise HTTPException(status_code=404, detail=f"Mbox file not found: {mbox_path}")

    # Start indexing in background
    background_tasks.add_task(index_mbox_background, mbox_path)

    return {
        "message": "Indexing started",
        "mbox_path": mbox_path,
        "status": "indexing"
    }


@app.get("/api/email/index/status")
async def get_indexing_status():
    """Get current indexing status"""
    return indexing_status


@app.get("/api/email/stats")
async def get_email_stats():
    """Get overall email archive statistics"""
    try:
        stats = await email_query.get_email_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")


@app.get("/api/email/search")
async def search_emails(
    query: Optional[str] = Query(None, description="Full-text search query"),
    sender: Optional[str] = Query(None, description="Filter by sender email"),
    recipient: Optional[str] = Query(None, description="Filter by recipient email"),
    subject: Optional[str] = Query(None, description="Filter by subject"),
    date_from: Optional[str] = Query(None, description="Start date (ISO format)"),
    date_to: Optional[str] = Query(None, description="End date (ISO format)"),
    has_attachments: Optional[bool] = Query(None, description="Filter by attachments"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """
    Search emails with various filters

    Returns:
        Paginated search results
    """
    try:
        results = await email_query.search_emails(
            query=query,
            sender=sender,
            recipient=recipient,
            subject=subject,
            date_from=date_from,
            date_to=date_to,
            has_attachments=has_attachments,
            limit=limit,
            offset=offset
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching emails: {str(e)}")


@app.get("/api/email/{email_id}")
async def get_email(email_id: int):
    """Get a single email by ID"""
    try:
        email = await email_query.get_email_by_id(email_id)
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
        return email
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching email: {str(e)}")


@app.get("/api/email/senders")
async def get_senders(limit: int = Query(100, ge=1, le=500)):
    """Get list of unique senders"""
    try:
        senders = await email_query.get_senders(limit)
        return {"senders": senders, "count": len(senders)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching senders: {str(e)}")


@app.get("/api/email/recipients")
async def get_recipients(limit: int = Query(100, ge=1, le=500)):
    """Get list of unique recipients"""
    try:
        recipients = await email_query.get_recipients(limit)
        return {"recipients": recipients, "count": len(recipients)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching recipients: {str(e)}")


# Analytics endpoints
@app.get("/api/email/analytics/by-year")
async def get_emails_by_year():
    """Get email count grouped by year"""
    try:
        results = await email_analytics.get_emails_by_year()
        return {"data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching analytics: {str(e)}")


@app.get("/api/email/analytics/by-month")
async def get_emails_by_month(year: Optional[int] = Query(None)):
    """Get email count grouped by month"""
    try:
        results = await email_analytics.get_emails_by_month(year)
        return {"data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching analytics: {str(e)}")


@app.get("/api/email/analytics/by-day")
async def get_emails_by_day_of_week():
    """Get email count grouped by day of week"""
    try:
        results = await email_analytics.get_emails_by_day_of_week()
        return {"data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching analytics: {str(e)}")


@app.get("/api/email/analytics/by-hour")
async def get_emails_by_hour():
    """Get email count grouped by hour of day"""
    try:
        results = await email_analytics.get_emails_by_hour()
        return {"data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching analytics: {str(e)}")


@app.get("/api/email/analytics/top-senders")
async def get_top_senders(limit: int = Query(20, ge=1, le=100)):
    """Get top senders by email count"""
    try:
        results = await email_analytics.get_top_senders(limit)
        return {"data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching analytics: {str(e)}")


@app.get("/api/email/analytics/top-recipients")
async def get_top_recipients(limit: int = Query(20, ge=1, le=100)):
    """Get top recipients by email count"""
    try:
        results = await email_analytics.get_top_recipients(limit)
        return {"data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching analytics: {str(e)}")


@app.get("/api/email/analytics/top-domains")
async def get_top_domains(
    limit: int = Query(20, ge=1, le=100),
    direction: str = Query("sender", regex="^(sender|recipient)$")
):
    """Get top email domains"""
    try:
        results = await email_analytics.get_top_domains(limit, direction)
        return {"data": results, "direction": direction}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching analytics: {str(e)}")


@app.get("/api/email/analytics/attachments")
async def get_attachment_statistics():
    """Get detailed attachment statistics"""
    try:
        results = await email_analytics.get_attachment_statistics()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching analytics: {str(e)}")


@app.get("/api/email/analytics/conversation/{email_address}")
async def get_conversation_statistics(email_address: str):
    """Get statistics for conversations with a specific email address"""
    try:
        results = await email_analytics.get_conversation_statistics(email_address)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching analytics: {str(e)}")


@app.get("/api/email/analytics/size")
async def get_size_statistics():
    """Get email size distribution statistics"""
    try:
        results = await email_analytics.get_size_statistics()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching analytics: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
