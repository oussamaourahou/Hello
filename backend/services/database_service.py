import os
from typing import List, Optional, Dict, Any
from supabase import create_client, Client
from datetime import datetime
import uuid


class DatabaseService:
    def __init__(self):
        """Initialize Supabase client"""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")

        # Allow optional Supabase - won't crash if not configured
        if not supabase_url or not supabase_key or supabase_url == "your_supabase_project_url_here":
            print("⚠️  Supabase not configured. Database endpoints will not work.")
            self.client = None
            self.storage_bucket = "palete-photos"
            return

        self.client: Client = create_client(supabase_url, supabase_key)
        self.storage_bucket = "palete-photos"

    # ==================== Restaurant Operations ====================

    async def create_restaurant(
        self,
        owner_user_id: str,
        name: str,
        cuisine_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new restaurant"""
        if not self.client:
            raise Exception("Supabase not configured. Please set SUPABASE_URL and SUPABASE_SERVICE_KEY in .env")

        data = {
            "owner_user_id": owner_user_id,
            "name": name,
            "cuisine_type": cuisine_type,
            "status": "draft"
        }

        result = self.client.table("restaurants").insert(data).execute()
        return result.data[0]

    async def get_restaurant(self, restaurant_id: str) -> Optional[Dict[str, Any]]:
        """Get a restaurant by ID"""
        result = self.client.table("restaurants").select("*").eq("id", restaurant_id).execute()
        return result.data[0] if result.data else None

    async def get_user_restaurants(self, owner_user_id: str) -> List[Dict[str, Any]]:
        """Get all restaurants for a user"""
        result = self.client.table("restaurants").select("*").eq("owner_user_id", owner_user_id).order("created_at", desc=True).execute()
        return result.data

    async def update_restaurant_status(
        self,
        restaurant_id: str,
        status: str
    ) -> Dict[str, Any]:
        """Update restaurant status (draft, processing, ready, exported)"""
        result = self.client.table("restaurants").update({"status": status}).eq("id", restaurant_id).execute()
        return result.data[0]

    async def delete_restaurant(self, restaurant_id: str) -> bool:
        """Delete a restaurant (cascade deletes menu items and photos)"""
        self.client.table("restaurants").delete().eq("id", restaurant_id).execute()
        return True

    # ==================== Menu Item Operations ====================

    async def create_menu_items(
        self,
        restaurant_id: str,
        items: List[str]
    ) -> List[Dict[str, Any]]:
        """Create multiple menu items from extraction"""
        data = [
            {
                "restaurant_id": restaurant_id,
                "name": item,
                "photo_source": "none"
            }
            for item in items
        ]

        result = self.client.table("menu_items").insert(data).execute()
        return result.data

    async def get_menu_items(self, restaurant_id: str) -> List[Dict[str, Any]]:
        """Get all menu items for a restaurant"""
        result = self.client.table("menu_items").select("*").eq("restaurant_id", restaurant_id).order("created_at").execute()
        return result.data

    async def update_menu_item_match(
        self,
        menu_item_id: str,
        matched_photo_id: str,
        confidence: int,
        reasoning: str,
        photo_source: str = "uploaded"
    ) -> Dict[str, Any]:
        """Update menu item with photo match data"""
        data = {
            "matched_photo_id": matched_photo_id,
            "match_confidence": confidence,
            "match_reasoning": reasoning,
            "photo_source": photo_source
        }

        result = self.client.table("menu_items").update(data).eq("id", menu_item_id).execute()
        return result.data[0]

    async def update_menu_item_quality(
        self,
        menu_item_id: str,
        quality_score: int,
        quality_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update menu item with quality assessment"""
        data = {
            "quality_score": quality_score,
            "quality_details": quality_details
        }

        result = self.client.table("menu_items").update(data).eq("id", menu_item_id).execute()
        return result.data[0]

    async def update_menu_item_enhanced_photo(
        self,
        menu_item_id: str,
        enhanced_photo_url: str
    ) -> Dict[str, Any]:
        """Update menu item with enhanced photo URL"""
        result = self.client.table("menu_items").update({
            "enhanced_photo_url": enhanced_photo_url
        }).eq("id", menu_item_id).execute()
        return result.data[0]

    async def get_menu_item(self, menu_item_id: str) -> Optional[Dict[str, Any]]:
        """Get a menu item by ID"""
        result = self.client.table("menu_items").select("*").eq("id", menu_item_id).execute()
        return result.data[0] if result.data else None

    # ==================== Photo Operations ====================

    async def create_photo(
        self,
        restaurant_id: str,
        filename: str,
        storage_path: str,
        source: str = "uploaded",
        generation_model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a photo record"""
        data = {
            "restaurant_id": restaurant_id,
            "filename": filename,
            "storage_path": storage_path,
            "source": source,
            "generation_model": generation_model
        }

        result = self.client.table("photos").insert(data).execute()
        return result.data[0]

    async def get_restaurant_photos(self, restaurant_id: str) -> List[Dict[str, Any]]:
        """Get all photos for a restaurant"""
        result = self.client.table("photos").select("*").eq("restaurant_id", restaurant_id).order("uploaded_at", desc=True).execute()
        return result.data

    async def get_photo(self, photo_id: str) -> Optional[Dict[str, Any]]:
        """Get a photo by ID"""
        result = self.client.table("photos").select("*").eq("id", photo_id).execute()
        return result.data[0] if result.data else None

    # ==================== Storage Operations ====================

    async def upload_photo_to_storage(
        self,
        file_path: str,
        restaurant_id: str,
        file_type: str = "original"
    ) -> str:
        """
        Upload a photo to Supabase Storage

        Args:
            file_path: Local path to the file
            restaurant_id: Restaurant ID for organizing files
            file_type: Type of file (original, enhanced, generated, thumbnail)

        Returns:
            Public URL of the uploaded file
        """
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = file_path.split(".")[-1]
        storage_filename = f"{restaurant_id}/{file_type}_{timestamp}_{uuid.uuid4().hex[:8]}.{file_extension}"

        # Read file
        with open(file_path, "rb") as f:
            file_data = f.read()

        # Upload to Supabase Storage
        self.client.storage.from_(self.storage_bucket).upload(
            storage_filename,
            file_data,
            file_options={"content-type": f"image/{file_extension}"}
        )

        # Get public URL
        public_url = self.client.storage.from_(self.storage_bucket).get_public_url(storage_filename)

        return public_url

    async def delete_photo_from_storage(self, storage_path: str) -> bool:
        """Delete a photo from Supabase Storage"""
        try:
            # Extract filename from full URL
            filename = storage_path.split(f"{self.storage_bucket}/")[-1]
            self.client.storage.from_(self.storage_bucket).remove([filename])
            return True
        except Exception:
            return False

    # ==================== Export Operations ====================

    async def get_restaurant_export_data(self, restaurant_id: str) -> Dict[str, Any]:
        """Get complete restaurant data for export"""
        # Get restaurant info
        restaurant = await self.get_restaurant(restaurant_id)

        # Get all menu items with joined photo data
        menu_items_result = self.client.table("menu_items").select(
            "*, matched_photo:photos!menu_items_matched_photo_id_fkey(*)"
        ).eq("restaurant_id", restaurant_id).execute()

        return {
            "restaurant": restaurant,
            "menu_items": menu_items_result.data,
            "exported_at": datetime.now().isoformat()
        }


# Singleton instance
_db_service = None

def get_database_service() -> DatabaseService:
    """Get or create the database service singleton"""
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService()
    return _db_service
