from swarm import Swarm, Agent
from dotenv import load_dotenv
import os
from typing import Dict


class PromptGenerator:
    """Handles conversion of story text into optimized image generation prompts"""

    def __init__(self):
        load_dotenv()
        self.client = Swarm()

        # Define categories and their identifying keywords
        self.categories = {
            "person": [
                "man",
                "woman",
                "person",
                "child",
                "warrior",
                "merchant",
                "traveler",
            ],
            "landscape": [
                "mountain",
                "forest",
                "field",
                "valley",
                "river",
                "lake",
                "ocean",
            ],
            "building": [
                "castle",
                "house",
                "temple",
                "ruins",
                "tower",
                "village",
                "city",
            ],
            "interior": [
                "room",
                "hall",
                "chamber",
                "tavern",
                "library",
                "dungeon",
            ],
            "object": [
                "sword",
                "book",
                "artifact",
                "treasure",
                "potion",
                "scroll",
            ],
            "creature": [
                "dragon",
                "wolf",
                "beast",
                "monster",
                "creature",
                "animal",
            ],
        }

        self.agent = Agent(
            name="Scene Summarizer",
            model="gpt-3.5-turbo",
            instructions="""
            Create extremely concise image generation prompts that fit within CLIP's 77 token limit.
            Identify the main subject category of the scene.

            Rules:
            1. Maximum 20 words total
            2. Focus on the main subject and one key action/state
            3. Add only the most important setting details
            4. End with only "high resolution image, cinematic lighting"
            5. Use weights sparingly - maximum two (subject:1.2) tags
            
            Return format:
            {
                "prompt": "your prompt here",
                "category": "person|landscape|building|interior|object|creature"
            }
            
            Example good:
            {
                "prompt": "(Explorer:1.2) examining ancient stone monument, moonlit ruins",
                "category": "person"
            }
            """,
        )

        # Add category-specific enhancement keywords
        self.category_enhancements = {
            "person": [
                "detailed facial features",
                "realistic skin texture",
                "natural pose",
                "expressive eyes",
                "detailed clothing folds",
                "anatomically correct",
            ],
            "landscape": [
                "atmospheric perspective",
                "detailed foliage",
                "natural lighting",
                "environmental storytelling",
                "realistic textures",
                "depth of field",
            ],
            "building": [
                "architectural details",
                "realistic materials",
                "proper perspective",
                "structural integrity",
                "weathering effects",
            ],
            "interior": [
                "ambient occlusion",
                "realistic lighting",
                "detailed furnishings",
                "proper perspective",
                "atmospheric depth",
            ],
            "object": [
                "fine details",
                "realistic materials",
                "proper scale",
                "surface texturing",
                "realistic reflections",
            ],
            "creature": [
                "anatomically plausible",
                "detailed scales/fur/skin",
                "realistic eyes",
                "natural pose",
                "proper proportions",
            ],
        }

        # Add category-specific negative prompts
        self.category_negatives = {
            "person": [
                "extra limbs",
                "deformed hands",
                "multiple heads",
                "wrong anatomy",
                "extra fingers",
                "mutation",
                "twisted body",
                "malformed limbs",
            ],
            "landscape": [
                "blurry background",
                "distorted perspective",
                "unnatural colors",
                "floating objects",
                "impossible geometry",
            ],
            "building": [
                "floating architecture",
                "impossible structures",
                "melting walls",
                "wrong perspective",
                "inconsistent scale",
            ],
            "interior": [
                "floating furniture",
                "impossible space",
                "wrong perspective",
                "inconsistent lighting",
                "melting objects",
            ],
            "object": [
                "deformed shape",
                "wrong scale",
                "floating parts",
                "impossible physics",
                "melting objects",
            ],
            "creature": [
                "extra limbs",
                "wrong anatomy",
                "multiple heads",
                "deformed body",
                "unnatural joints",
                "impossible biology",
            ],
        }

        # Base negative prompt that applies to all categories
        self.base_negative = """text, watermark, logo, title, signature, 
            blurry, low quality, distorted, deformed, disfigured, 
            out of frame, duplicate, meme, cartoon, anime"""

        # Add style presets
        self.style_preset = (
            "epic fantasy art, detailed, cinematic, atmospheric"
        )

    def create_prompt(
        self, story_text: str, previous_story: str = None, style: str = None
    ) -> dict:
        """Convert story text into a complete image generation prompt"""
        context = ""
        if previous_story:
            context = f"{previous_story}\n"
        context += story_text

        # Get base prompt and category from GPT
        response = self.client.run(
            agent=self.agent,
            messages=[
                {
                    "role": "user",
                    "content": f"Create a concise image prompt (max 20 words) with category for this scene:\n{context}",
                }
            ],
        )

        try:
            import json

            result = json.loads(response.messages[0]["content"])
            base_prompt = result["prompt"]
            category = result["category"]

            # Add environmental details
            enhanced_base = self._enhance_prompt(base_prompt)

            # Get category-specific enhancements
            enhancements = ", ".join(
                self.category_enhancements.get(category, [])[:3]
            )

            # Get category-specific negative prompts
            category_negatives = ", ".join(
                self.category_negatives.get(category, [])
            )
            negative_prompt = f"{self.base_negative}, {category_negatives}"

            # Use provided style or default
            style = style or self.style_preset

            # Build final prompt
            final_prompt = f"""masterpiece digital art, {enhanced_base}, {style}, 
                {enhancements}, volumetric lighting, dramatic composition, 
                detailed foreground and background elements,
                professional photography, award winning"""

            print(
                f"\033[91m -  - IMAGE PROMPT -  - \033[0m\n"
                f"Base prompt: {base_prompt}\n"
                f"Enhancements: {enhancements}\n"
                f"Style: {style}\n"
                f"Category: {category}\n"
                f"Negative prompt: {negative_prompt}\n"
                f"Final prompt: {final_prompt}\n"
            )

            return {
                "prompt": final_prompt,
                "negative_prompt": negative_prompt,
            }

        except Exception as e:
            print(f"Error creating prompt: {e}")
            # Return basic prompts as fallback
            return {
                "prompt": f"masterpiece digital art, {story_text}, {self.style_preset}",
                "negative_prompt": self.base_negative,
            }

    def _enhance_prompt(self, base_prompt: str) -> str:
        """Add missing environmental details to the prompt"""
        # Extract key elements
        time_indicators = [
            "night",
            "day",
            "sunset",
            "sunrise",
            "dawn",
            "dusk",
        ]
        weather_conditions = [
            "rain",
            "storm",
            "clear sky",
            "cloudy",
            "misty",
            "foggy",
        ]

        # Check what's missing
        has_time = any(
            time in base_prompt.lower() for time in time_indicators
        )
        has_weather = any(
            weather in base_prompt.lower() for weather in weather_conditions
        )

        # Build enhanced prompt
        enhanced = base_prompt.strip()

        # Add establishing shot indicator if not present
        if "establishing shot" not in enhanced.lower():
            enhanced = "establishing shot, " + enhanced

        # Add time of day if missing
        if not has_time and "night" not in enhanced.lower():
            enhanced += ", daytime scene"

        # Add weather if missing
        if not has_weather:
            enhanced += ", clear atmosphere"

        return enhanced
