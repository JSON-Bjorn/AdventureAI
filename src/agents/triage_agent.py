import os
import sys
import asyncio
from swarm import Swarm, Agent
from dotenv import load_dotenv

# Add project root to Python path
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.append(project_root)

"""
Placeholder for triage agent instructions


                "3. Take the output from author agent "
                "and hand it to the illustrator agent. \n"
                "Illustrator agent will then generate an image.\n"
                "4. Take the output from author agent "
                "and hand it to the navigator agent. \n"
                "Navigator agent will then determine the location of the story."
"""
"""
The triage agent class is the handler of user input and AI output by passing
information between agent, effectively breaking down the task into smaller chunks.

Agents:
- Triage, handles all agents
- Author, generates the next story.
- Illustrator, generates images based on story. (Not an agent ATM)
- Navigator, figures out where we are.
- Dice roller, determines if an action needs to be rolled for.



Flow of the game:
Upon start:
- Game is started and this class is instantiated.
- Pipeline to Stable Diffusion it set up for image generation.
- We gather user-information and store in instance variables.

The game loop:
- User information, context about the previous story, 
  player choice and success is sent to the Author.
- Author generates a new story based on it's input.
  Return the new story to Triage.
- The new story is fed to the Illustrator (currently not an agent).
  An image is generated using Stable Diffusion and returned to Triage.
- The new story is passed of to the Navigator who then determines where
  we are and returns a location to Triage.
- The user is prompted to make an action.
- The dice roller analyzes the action and determines the difficulty on a scale
  of 1-20 (simulating a D20 dice).
- The user is prompted to roll (randomly generates a number).
  If the user rolls equal or above the threshhold, their action was successful.
- User action, success (bool), story context and user information is then
  packaged together and the cycle continues.
"""


class TriageAgent:
    def __init__(self, author, narrator, illustrator, mood_analyzer):
        load_dotenv()
        self.author = author.agent  # TextAgent still uses Swarm
        self.narrator = narrator  # SoundAgent now used directly
        self.illustrator = illustrator
        self.client = Swarm()
        self.agent = Agent(
            name="Dungeon Master",
            model="gpt-4o-mini",
            instructions=(
                "You are a triage agent that connects several "
                "agents working together to write a story for a video game.\n"
                "Your task is to pass information "
                "between agents that generate content.\n"
                "Your input will be a string consisting "
                "of a story, player choice, player success."
                "You should do things in this order:\n"
                "1. Give the entire input string to the author agent. "
                "Author agent will then generate the next step in the story.\n"
                "please work with what you have for now."
                "2. Take the output from author agent "
                "and hand it to the narrator agent. \n"
                "Narrator agent will then generate a sound file.\n"
                "If no content is available to send to the narrator agent, send them this:"
                "'Once upon a fucking time, this and that. EXPLOSIONS!'"
                "As for now, you are in production and are missing some instructions, "
            ),
            functions=[
                self._transfer_to_author,
                self._transfer_to_illustrator,
                self._transfer_to_narrator,
            ],
        )
        # Story state
        self.story_history = []
        self.current_story = None
        self.player_choice = None
        self.success = None
        self.current_image = None
        self.current_voiceover = None
        self.mood_analyzer = mood_analyzer
        self.context_window = (
            4  # Number of previous story segments to remember
        )
        # Initialize with default mood and intensity
        self.current_intensity = 1
        self.current_mood = "adventerous"

    # =====Class, return and transfer methods===== #
    @classmethod
    async def create(cls, author, narrator, illustrator, mood_analyzer):
        self = cls(author, narrator, illustrator, mood_analyzer)
        await self._initialize_image_pipeline()
        return self

    def _transfer_to_author(self):
        """Transfers to the author agent"""
        return self.author.agent

    def _transfer_to_illustrator(self):
        """Transfers to the author agent"""
        return self.illustrator.agent

    def _transfer_to_narrator(self):
        """Transfers to the author agent"""
        return self.narrator.agent

    def get_text(self):
        return self.current_story

    def get_voiceover(self):
        return self.current_voiceover

    def get_image(self):
        return self.current_image

    # =====Gameplay methods===== #
    async def next_story(self):
        """Generate the next part of the story based on player's choice and outcome"""
        # Build context with last few story segments
        recent_history = (
            self.story_history[-self.context_window :]
            if self.story_history
            else []
        )

        # Format recent history into a readable context
        history_text = ""
        for i, entry in enumerate(recent_history, 1):
            history_text += f"Story {i}: {entry['story']}\n"
            history_text += f"Player action: {entry['player_choice']}\n"
            history_text += f"Success: {entry['success']}\n\n"

        # Build context for the author
        context = {
            "story_history": self.story_history,
            "recent_history": history_text,
            "previous_story": self.current_story,
            "player_choice": self.player_choice,
            "player_choice_successful": self.success,
        }

        # Get next story segment from author with expanded context
        response = self.client.run(
            agent=self.author,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Recent story history:\n{history_text}\n"
                        f"Current story: {self.current_story}\n"
                        f"Player chose to: {self.player_choice}\n"
                        f"Player succeeded: {self.success}"
                    ),
                }
            ],
            context_variables=context,
        )

        # Store new story
        new_story = response.messages[0]["content"]
        if self.current_story:
            self.story_history.append(
                {
                    "story": self.current_story,
                    "player_choice": self.player_choice,
                    "success": self.success,
                }
            )
        self.current_story = new_story

        # Analyze scene intensity and mood, then update music
        intensity, mood = self.mood_analyzer.analyze_scene(new_story)

        # Only update music if intensity or mood has changed
        if intensity != self.current_intensity or mood != self.current_mood:
            self.narrator.play_background_music(
                intensity=intensity, mood=mood
            )
            self.current_intensity = intensity
            self.current_mood = mood

        # Generate audio for the new story
        await self.narrator.generate_speech(new_story)
        self.current_voiceover = self.narrator

        # Generate image for new story
        await self._generate_image()

        # Reset player action state
        self.player_choice = None
        self.success = None

    # ===== Image generation ===== #
    async def _initialize_image_pipeline(self):
        await self.illustrator.initialize()

    async def _generate_image(self):
        print("Generating image..")
        if not self.current_story:
            raise ValueError(
                "No prompt(story) available for image generation"
            )

        # Create a summarized scene description for image generation
        scene_summary = self._summarize_scene_for_image()

        image = await self.illustrator.generate_scene_image(
            description=scene_summary,
            width=768,  # Changed from 512
            height=768,  # Changed from 768
        )

        if image:
            self.current_image = image
        else:
            print("Failed to generate image.")

    def _summarize_scene_for_image(self) -> str:
        """
        Create an optimized image generation prompt following Juggernaut's guidelines.
        """
        # Get scene context from story history if available
        context = ""
        if self.story_history:
            last_story = self.story_history[-1]["story"]
            context = f"{last_story}\n"

        # Add current story
        if self.current_story:
            context += self.current_story

        # Use GPT to create a visual summary
        response = self.client.run(
            agent=Agent(
                name="Scene Summarizer",
                model="gpt-3.5-turbo",
                instructions="""
                Create extremely concise image generation prompts that fit within CLIP's 77 token limit.

                Rules:
                1. Maximum 30 words total
                2. Focus on the main subject and one key action/state
                3. Add only the most important setting details
                4. End with only "high resolution image, cinematic lighting"
                5. Use weights sparingly - maximum two (subject:1.2) tags
                
                Example good (under token limit):
                "(Explorer:1.2) examining ancient stone monument, (ornate carvings:1.1), moonlit ruins, high resolution image, cinematic lighting"
                
                Example bad (too long):
                "(Explorer:1.2) uncovering tarnished silver locket with (Lady's picture:1.1), moonlit jungle path revealed, eerie palm shadows, glimmering object in sand, volumetric lighting, dramatic composition, high resolution image, cinematic lighting"
                """,
            ),
            messages=[
                {
                    "role": "user",
                    "content": f"Create a concise image prompt (max 30 words) for this scene:\n{context}",
                }
            ],
        )

        summary = response.messages[0]["content"]
        print(f"Generated image prompt: {summary}")
        return summary
