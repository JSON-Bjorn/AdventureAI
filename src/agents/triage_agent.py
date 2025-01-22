from swarm import Swarm, Agent
from dotenv import load_dotenv
import asyncio

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
    def __init__(self, author, narrator, illustrator):
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

    # =====Class, return and transfer methods===== #
    @classmethod
    async def create(cls, author, narrator, illustrator):
        self = cls(author, narrator, illustrator)
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
        # Build context for the author
        context = {
            "story_history": self.story_history,
            "previous_story": self.current_story,
            "player_choice": self.player_choice,
            "player_choice_successful": self.success,
        }

        # Get next story segment from author
        response = self.client.run(
            agent=self.author,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Previous story: {self.current_story}\n"
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
                You are a prompt engineer for AI image generation. Create precise, structured prompts
                following these rules:

                Core Components (in order):
                1. Subject: Main focus (person, creature, object)
                2. Action/State: What they're doing
                3. Environment: The setting or background
                4. Key Details: Important visual elements
                5. Style/Quality Tags: End with these

                Rules:
                - Keep total length under 40 words
                - Start with the most important element
                - Use clear, specific descriptions
                - Add weights to important elements using (element:1.2) format
                - End with "high resolution image, cinematic lighting"
                
                Example input:
                "Keeping your nerves steady and your eyes sharp, you inspected the monument carefully, 
                your hands brushing over its cold, age-worn surface. The fear of what might linger in 
                the darkness steeled your resolve. Your fingers grazed over an ornate carving, veiled 
                by the night's embrace. The stone groaned, and suddenly a panel slid back, revealing 
                an arsenal of ancient weapons."
                
                Example output:
                "(Explorer:1.2) examining ancient stone monument with (ornate carvings:1.1), hidden weapon chamber revealed, 
                moonlit ruins, dramatic shadows, high resolution image, cinematic lighting"
                """,
            ),
            messages=[
                {
                    "role": "user",
                    "content": f"Create an image generation prompt for this scene:\n{context}",
                }
            ],
        )

        summary = response.messages[0]["content"]
        print(f"Generated image prompt: {summary}")
        return summary
