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
        background_color: str = "white"
    ) -> PhotoroomEnhancementResult:
        """
        Stage 4: Enhance photo using Photoroom API

        Args:
            image_path: Path to the food photo
            background_color: Background color (default: white)

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

        data = {
            "background.color": background_color,
            "outputSize": "1024x1024"
        }

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
                transformations_applied=[
                    "Background removal",
                    f"Background color: {background_color}",
                    "Standardized size: 1024x1024"
                ]
            )
