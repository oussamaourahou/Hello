import os
from openai import OpenAI, OpenAIError, AuthenticationError, RateLimitError, APIError
import httpx
import uuid


class ImageGenerationService:
    def __init__(self):
        """Initialize image generation service with OpenAI DALL-E"""
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)

    async def generate_food_image(self, dish_name: str, cuisine_style: str = None) -> dict:
        """
        Generate a professional food photo using DALL-E 3

        Args:
            dish_name: Name of the dish to generate
            cuisine_style: Optional cuisine style (e.g., "Moroccan", "French", "Nordic")

        Returns:
            dict with image_url and prompt_used
        """

        # Follow official UberEats/Glovo photo guidelines
        # Based on merchant photo requirements for delivery apps
        cuisine_context = f"{cuisine_style} " if cuisine_style else ""

        prompt = f"""A straightforward menu photo of {dish_name} on a plain white plate.
Top-down view, centered in frame.
Natural window light, no dramatic shadows or highlights.
Clean white plate, neutral light gray background.
The food exactly as it would be delivered - realistic portions.
No garnishes, no herbs, no decorative elements, no props.
No hands, no utensils, no side dishes visible.
No patterns on the plate, no textured surfaces.
Simple, honest food photo for a delivery app menu.
Not artistic, not styled - just clear and appetizing."""

        try:
            # Generate image with DALL-E 3 (premium quality: $0.04 per image)
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",  # Use "hd" for even better quality at $0.08/image
                n=1,
            )

            image_url = response.data[0].url

            # Download the image to save locally
            local_path = await self._download_image(image_url, dish_name)

            return {
                "image_url": local_path,
                "prompt_used": prompt,
                "dish_name": dish_name,
                "generation_model": "dall-e-3"
            }

        except AuthenticationError:
            raise Exception(
                "OpenAI API key is invalid or expired. Please check your API key at https://platform.openai.com/api-keys"
            )
        except RateLimitError:
            raise Exception(
                "OpenAI API rate limit exceeded. Please wait a moment or upgrade your plan."
            )
        except APIError as e:
            if "billing" in str(e).lower():
                raise Exception(
                    "OpenAI billing issue. Please check your billing at https://platform.openai.com/account/billing"
                )
            raise Exception(f"OpenAI API error: {str(e)}")
        except OpenAIError as e:
            raise Exception(f"Image generation error: {str(e)}")

    async def _download_image(self, image_url: str, dish_name: str) -> str:
        """Download generated image and save locally"""

        # Create uploads directory if it doesn't exist
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)

        # Generate unique filename
        safe_dish_name = "".join(c for c in dish_name if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_dish_name = safe_dish_name.replace(' ', '_')
        filename = f"generated_{safe_dish_name}_{uuid.uuid4().hex[:8]}.png"
        file_path = os.path.join(upload_dir, filename)

        # Download image
        async with httpx.AsyncClient() as client:
            response = await client.get(image_url)
            response.raise_for_status()

            with open(file_path, 'wb') as f:
                f.write(response.content)

        return file_path
