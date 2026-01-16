import os
import httpx
from backend.models.schemas import PhotoroomEnhancementResult


class PhotoroomService:
    def __init__(self):
        self.api_key = os.getenv("PHOTOROOM_API_KEY")
        self.base_url = "https://sdk.photoroom.com/v1/segment"

    async def enhance_photo(
        self,
        image_path: str,
        background_style: str = "white"
    ) -> PhotoroomEnhancementResult:
        """
        Stage 4: Enhance photo using Photoroom API with AI Food mode

        Args:
            image_path: Path to the food photo
            background_style: Background style - "white", "wooden_table", "plate", or custom color

        Returns:
            PhotoroomEnhancementResult with enhanced image URL
        """

        # Read the image file
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()

        # Prepare the request
        headers = {
            "x-api-key": self.api_key
        }

        files = {
            "image_file": ("image.jpg", image_data, "image/jpeg")
        }

        # Enhanced parameters for food photography
        data = {
            # AI Food mode for food-specific beautification
            "ai.food": "true",

            # Background settings
            "background.color": background_style if background_style in ["white", "black"] else "white",

            # Image enhancements
            "outputSize": "1024x1024",

            # Shadow for depth and realism
            "shadow.mode": "ai.auto",

            # Padding for better composition
            "padding": "0.1"
        }

        transformations = [
            "AI Food Enhancement (sharpness, color, lighting)",
            "Background removal and replacement",
            f"Background: {background_style}",
            "Automatic shadow generation",
            "Standardized size: 1024x1024"
        ]

        # Call Photoroom API
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.base_url,
                headers=headers,
                files=files,
                data=data
            )

            if response.status_code != 200:
                raise Exception(f"Photoroom API error: {response.text}")

            # Save the enhanced image
            enhanced_image_path = image_path.replace(".", "_enhanced.")

            with open(enhanced_image_path, "wb") as f:
                f.write(response.content)

            return PhotoroomEnhancementResult(
                enhanced_image_url=enhanced_image_path,
                original_image_url=image_path,
                transformations_applied=transformations
            )
