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

    def create_prompt(
        self, story_text: str, previous_story: str = None
    ) -> Dict[str, str]:
        """Convert story text into an optimized image generation prompt with category"""
        context = ""
        if previous_story:
            context = f"{previous_story}\n"
        context += story_text

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

            enhanced_prompt = self._enhance_prompt(base_prompt)
            print(
                f"\033[31mFull prompt:\033[0m {enhanced_prompt} (Category: {category})"
            )

            return {"prompt": enhanced_prompt, "category": category}
        except Exception as e:
            return {
                "prompt": self._enhance_prompt(
                    response.messages[0]["content"]
                ),
                "category": "landscape",  # Default fallback
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
