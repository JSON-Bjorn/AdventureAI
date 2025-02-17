from swarm import Swarm, Agent
from dotenv import load_dotenv


class MoodAnalyzer:
    def __init__(self):
        load_dotenv()
        self.client = Swarm()
        self.agent = Agent(
            name="Mood Analyzer",
            model="gpt-3.5-turbo",
            instructions="""
You are a scene intensity and mood analyzer for a video game. Your task is to analyze story text 
and determine both the intensity level (1-3) and the specific mood category.

Intensity Levels and Moods:
1 (Calm):
    - adventerous: Bold exploration, discovery, excitement without danger
    - dreamy: Peaceful, ethereal, contemplative moments
    - mystical: Ancient places, magic, wonder
    - serene: Peaceful, safe, tranquil moments

2 (Medium):
    - lurking: Hidden dangers, something watching
    - nervous: Uncertainty, mild anxiety
    - ominous: Foreboding, dark omens
    - playful: Light mischief, fun challenges
    - quirky: Strange but not threatening
    - upbeat: Positive energy with mild tension

3 (Intense):
    - chaotic: Wild, unpredictable situations
    - combat: Fighting, battles
    - epic: Grand, dramatic moments
    - scary: Horror, terror, immediate danger

Return ONLY a JSON object with two fields:
{
    "intensity": 1/2/3,
    "mood": "category_name"
}

Example: {"intensity": 2, "mood": "ominous"}
""",
        )

    def analyze_scene(self, story_text: str) -> tuple[int, str]:
        """Analyze the story text and return intensity level and mood"""
        try:
            response = self.client.run(
                agent=self.agent,
                messages=[
                    {
                        "role": "user",
                        "content": f"Analyze this scene and return the intensity and mood as JSON:\n{story_text}",
                    }
                ],
            )

            # Parse the JSON response
            import json

            result = json.loads(response.messages[0]["content"].strip())

            intensity = result["intensity"]
            mood = result["mood"]

            # Validate intensity
            if intensity not in [1, 2, 3]:
                print(
                    f"Warning: Invalid intensity {intensity}, defaulting to 1"
                )
                intensity = 1

            # Validate mood based on intensity
            valid_moods = {
                1: ["adventerous", "dreamy", "mystical", "serene"],
                2: [
                    "lurking",
                    "nervous",
                    "ominous",
                    "playful",
                    "quirky",
                    "upbeat",
                ],
                3: ["chaotic", "combat", "epic", "scary"],
            }

            if mood not in valid_moods[intensity]:
                print(
                    f"Warning: Invalid mood {mood} for intensity {intensity}"
                )
                mood = valid_moods[intensity][0]

            print(f"Scene analysis: Intensity {intensity}, Mood: {mood}")
            return intensity, mood

        except Exception as e:
            print(f"Error analyzing scene mood: {e}")
            return (
                1,
                "adventerous",
            )  # Default to calm adventerous if analysis fails
