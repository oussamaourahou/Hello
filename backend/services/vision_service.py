import base64
import os
from typing import List
from openai import OpenAI
from backend.models.schemas import PhotoMatchResult, PhotoQualityAssessment, MenuExtractionResult
from pdf2image import convert_from_path
from PIL import Image
import io


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

        prompt = f"""You are an EXPERT food identification AI for Glovo restaurant menu management.

STRICT MATCHING RULES:
1. You MUST match to EXACTLY ONE item from the menu list below
2. Use ONLY the EXACT name from the list (no variations or modifications)
3. If the dish doesn't clearly match ANY item, set confidence < 40
4. Be STRICT - better to have low confidence than wrong match

MENU ITEMS:
{menu_list}

CUISINE CONTEXT & IDENTIFICATION CRITERIA:
Common breakfast items and their typical characteristics:

**Breakfast Beldi** (Traditional Moroccan):
- Bread: Msemen, Batbout, Khobz, Harcha, Baghrir
- Proteins: Eggs (often sunny-side), cheese, olives
- Accompaniments: Olive oil, honey, amlou, fresh cheese
- Presentation: Traditional tagine, rustic serving

**Breakfast Norvégien** (Scandinavian/Nordic):
- Proteins: Smoked salmon, herring, gravlax
- Bread: Dark rye, crisp bread
- Accompaniments: Cream cheese, dill, capers, red onion
- Presentation: Elegant, minimalist plating

**Breakfast Gourmande** (French Gourmet):
- Bread: Croissants, pain au chocolat, baguette
- Proteins: Poached eggs, soft-boiled eggs
- Presentation: Refined, artistic plating
- Accompaniments: Fine cheeses, jams, butter

**Breakfast British** (Traditional English):
- Proteins: Bacon, sausages, eggs (fried/scrambled)
- Accompaniments: Baked beans, grilled tomatoes, mushrooms, toast
- Presentation: Hearty, full plate

**Breakfast Espagnol** (Spanish):
- Proteins: Chorizo, jamón, eggs
- Bread: Pan con tomate, tostada
- Accompaniments: Tomatoes, peppers, potatoes
- Presentation: Colorful, tapas-style

**Breakfast Protéiné** (High-Protein/Fitness):
- Proteins: Grilled chicken, egg whites, Greek yogurt, protein powder
- Carbs: Minimal or complex (oats, sweet potato)
- Presentation: Clean, portion-controlled, fitness-focused

CONFIDENCE SCORING (BE STRICT):
- 90-100: Perfect match - ALL key elements align (bread type, proteins, presentation style, cultural markers)
- 70-89: Strong match - MOST key elements align clearly
- 50-69: Probable match - SOME key elements align, but missing important markers
- 30-49: Weak match - Minimal alignment, significant doubt
- 0-29: No clear match - Does not fit any menu item

ANALYSIS PROCESS:
1. Identify ALL visible elements: bread type, proteins, eggs style, garnishes, presentation
2. Compare against EACH menu item's typical characteristics
3. Determine best match based on cultural cuisine markers
4. Assign confidence based on how many elements align
5. If unsure between items, LOWER the confidence score

OUTPUT FORMAT (JSON):
{{
    "dish_identified": "detailed description of what you see in the image",
    "matched_item": "EXACT name from menu list above",
    "confidence": 75,
    "description": "appetizing 2-3 sentence description of the dish",
    "reasoning": "detailed explanation of why this match was chosen, mentioning specific visual elements"
}}

BE STRICT. Better to have low confidence than wrong match."""

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

    async def extract_menu_items(
        self,
        file_path: str,
        is_pdf: bool = False
    ) -> MenuExtractionResult:
        """
        Stage 1: Extract menu items from PDF or image

        Args:
            file_path: Path to the menu file (PDF or image)
            is_pdf: Whether the file is a PDF

        Returns:
            MenuExtractionResult with extracted menu items
        """

        # Convert PDF to image if needed
        if is_pdf:
            # Convert PDF to images (take first page only for now)
            images = convert_from_path(file_path, first_page=1, last_page=1)

            # Save the first page as temporary image
            temp_image_path = file_path.replace('.pdf', '_page1.jpg')
            images[0].save(temp_image_path, 'JPEG')
            image_path = temp_image_path
        else:
            image_path = file_path

        # Encode the image
        base64_image = self.encode_image(image_path)

        prompt = """You are an expert menu data extraction AI for restaurant menu management.

Your task is to extract ONLY the menu item names from this menu image.

EXTRACTION RULES:
1. Extract ONLY the item names (e.g., "Breakfast Beldi", "Croissant", "Pancakes")
2. DO NOT include prices, descriptions, or ingredients
3. DO NOT include section headers like "Breakfast", "Lunch", "Desserts" unless they are part of the item name
4. Extract items in the order they appear on the menu
5. If an item has variants (e.g., "Coffee Small", "Coffee Large"), list each variant separately
6. Preserve the exact spelling and capitalization from the menu
7. Skip any promotional text, disclaimers, or restaurant information

EXAMPLES:
Good: ["Breakfast Beldi", "Breakfast Norvégien", "Pancakes with Maple Syrup"]
Bad: ["Breakfast Section", "Beldi - Traditional Moroccan breakfast with eggs", "$12.99"]

Respond in JSON format:
{
    "menu_items": ["Item 1", "Item 2", "Item 3"],
    "total_items": 3,
    "extraction_notes": "Brief note about the extraction (e.g., 'Found 15 breakfast items' or 'Menu appears to be in French')"
}

BE PRECISE. Extract only actual menu item names."""

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
            max_tokens=1000,
            response_format={"type": "json_object"}
        )

        # Parse the response
        import json
        result = json.loads(response.choices[0].message.content)

        # Clean up temp file if PDF was converted
        if is_pdf and os.path.exists(image_path):
            os.remove(image_path)

        return MenuExtractionResult(
            menu_items=result.get("menu_items", []),
            total_items=result.get("total_items", 0),
            extraction_notes=result.get("extraction_notes", "")
        )
