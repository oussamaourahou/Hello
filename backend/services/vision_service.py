import base64
import os
from typing import List
from openai import OpenAI
from backend.models.schemas import PhotoMatchResult, PhotoQualityAssessment


class VisionService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def encode_image(self, image_path: str) -> str:
        """Encode image to base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    async def match_photo_to_menu(
        self,
        image_path: str,
        menu_items: List[str]
    ) -> PhotoMatchResult:
        """
        Stage 2: Match a food photo to menu items using GPT-4 Vision

        Args:
            image_path: Path to the uploaded food photo
            menu_items: List of menu item names

        Returns:
            PhotoMatchResult with matched item, confidence, and description
        """

        # Encode the image
        base64_image = self.encode_image(image_path)

        # Create the prompt
        menu_list = "\n".join([f"- {item}" for item in menu_items])

        prompt = f"""You are an expert food identification AI for a restaurant menu management system.

Analyze this food photo and match it to one of the following menu items:

{menu_list}

Your task:
1. Identify what dish is shown in the photo
2. Match it to the MOST LIKELY item from the menu list above
3. Provide a confidence score (0-100)
4. Write a detailed, appetizing description of the dish (2-3 sentences)
5. Explain your reasoning for the match

Respond in JSON format:
{{
    "dish_identified": "what you see in the image",
    "matched_item": "exact name from the menu list",
    "confidence": 85,
    "description": "appetizing description of the dish",
    "reasoning": "why this match makes sense"
}}

Be specific and use culinary terms. If the match is uncertain, lower the confidence score accordingly."""

        # Call OpenAI Vision API
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500,
            response_format={"type": "json_object"}
        )

        # Parse the response
        import json
        result = json.loads(response.choices[0].message.content)

        return PhotoMatchResult(
            dish_identified=result.get("dish_identified", "Unknown"),
            matched_item=result.get("matched_item", menu_items[0] if menu_items else "Unknown"),
            confidence=result.get("confidence", 0),
            description=result.get("description", ""),
            reasoning=result.get("reasoning", "")
        )

    async def assess_photo_quality(self, image_path: str) -> PhotoQualityAssessment:
        """
        Stage 3: Assess photo quality against Glovo standards

        Args:
            image_path: Path to the food photo

        Returns:
            PhotoQualityAssessment with detailed scores
        """

        # Encode the image
        base64_image = self.encode_image(image_path)

        prompt = """You are a professional food photography quality assessor for Glovo.

Evaluate this food photo on the following criteria (each scored 0-100):

1. **Resolution**: Is the image sharp and high-resolution? (minimum 800x800px recommended)
2. **Lighting**: Is the food well-lit with natural, appealing lighting?
3. **Composition**: Is the dish properly framed and centered?
4. **Presentation**: Does the food look fresh, appetizing, and well-presented?

Based on these scores, classify the photo as:
- "Ready": Can be used immediately (overall score 75+)
- "Needs Enhancement": Usable but could be improved (50-74)
- "Reject": Not suitable, needs new photo (<50)

Provide a brief recommendation for improvement if needed.

Respond in JSON format:
{
    "resolution_score": 85,
    "lighting_score": 90,
    "composition_score": 80,
    "presentation_score": 95,
    "overall_score": 87,
    "overall_quality": "Ready",
    "recommendation": "Photo is excellent and ready to use."
}"""

        # Call OpenAI Vision API
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=300,
            response_format={"type": "json_object"}
        )

        # Parse the response
        import json
        result = json.loads(response.choices[0].message.content)

        return PhotoQualityAssessment(
            resolution_score=result.get("resolution_score", 0),
            lighting_score=result.get("lighting_score", 0),
            composition_score=result.get("composition_score", 0),
            presentation_score=result.get("presentation_score", 0),
            overall_score=result.get("overall_score", 0),
            overall_quality=result.get("overall_quality", "Reject"),
            recommendation=result.get("recommendation", "")
        )
