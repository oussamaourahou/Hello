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

        # Build ultra-realistic prompt for Moroccan restaurant food photography
        # Focus on authentic, appetizing, non-AI looking results
        cuisine_context = f"{cuisine_style} " if cuisine_style else "Moroccan "

        prompt = f"""A mouthwatering photo of {cuisine_context}{dish_name} served at a premium Casablanca restaurant.
The dish is beautifully plated on traditional white ceramic tableware with subtle Moroccan patterns on the rim.
Shot in natural morning light streaming through arched windows, creating soft shadows that enhance the food's texture and colors.
The composition shows the dish from a slight overhead angle (45 degrees),
with authentic garnishes like fresh mint leaves, sesame seeds, or a drizzle of argan oil.
The background is minimalist - a clean white marble table with a subtle texture.
The photo captures steam rising from hot dishes, glistening olive oil, and the rich, vibrant colors of fresh ingredients.
Professional food photography with shallow depth of field, sharp focus on the main dish,
warm color temperature, and realistic lighting that makes the food look irresistibly appetizing.
The image should look like it was shot by a professional food photographer for Glovo Morocco's premium restaurant section,
not AI-generated - authentic, natural, and making viewers immediately want to order this dish."""

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
