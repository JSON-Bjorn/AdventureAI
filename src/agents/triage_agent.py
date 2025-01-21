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
        self.author = author.agent
        self.narrator = narrator.agent
        self.illustrator = illustrator
        self.client = (
            Swarm()
        )  # Swarm automatically uses OPENAI_API_KEY from env
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
        # Player information should be moved to database:
        self.player_name = None
        self.player_description = None
        # This should stay here
        self.previous_story = "This is the start of our protagonists journey!"
        self.current_story = None
        self.current_location = None
        self.choice = None
        self.success = True  # Lets be nice in the tutorial
        self.current_image = None
        self.current_voiceover = None
        self.context_string = None

    # =====Class, return and transfer methods===== #
    @classmethod
    async def create(cls, author, narrator, illustrator):
        self = cls(author, narrator, illustrator)
        await self._initialize_image_pipeline()
        self.new_player()
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
    def new_player(self):
        # self.player_name = input("What is your name?\n > ")
        # self.player_description = input("Tell us about yourself!\n > ")
        # self.current_location = input("Where does your story begin? \n > ")
        # self.choice = input("And what would you like to do?\n > ")

        self.player_name = "Felix"
        self.player_description = "Im a very shy boy"
        self.current_location = "Paris"
        self.choice = "I want to eat a baugette"

    async def next_story(self):
        self._set_context()
        response = self._make_api_call()
        self._extract_response(response)
        if self.current_story:
            await self._generate_image()
        else:
            print("No current story to generate image from.")

    def player_turn(self):
        self.choice = input(f"\nWhat does {self.player_name} do next?\n > ")
        if self.choice == "":
            self.choice = "I start screaming 'I HAVE NO IMAGINATION!'"

        return self.choice

    def _set_context(self):
        self.context_string = (
            f"Protagonist name: {self.player_name}\n"
            f"Protagonist description: {self.player_description}\n"
            f"Current location: {self.current_location}"
            f"Previous story: {self.previous_story}"
            f"{self.player_description} said they want to: '{self.choice}'\n"
            f"{self.player_description} was successful with their action = {self.success}"
        )

    # ===== API and responses ===== #
    def _make_api_call(self) -> str:
        response = self.client.run(
            agent=self.author,  # This is the bug. We are only using the autor agent in out api call
            messages=[
                {
                    "role": "user",
                    "content": self.context_string,
                }
            ],
            # Seems our agent can't access context variables
            context_variables={
                "previous_story": self.previous_story,
                "player_choice": self.choice,
                "player_choice_successful": self.success,
            },
        )

        return response

    def _extract_response(self, response) -> str:
        """THIS NEEDS TO BE CALIBRATED TO FIT THE NEW RESPONSE WITH MULTIPLE AGENTS"""
        for message in response.messages:
            if message["sender"] == "The Author":
                self.current_story = message["content"]
                continue

            if message["sender"] == "The Narrator":
                self.current_voiceover = message["content"]
                continue

            if message["sender"] == "The Illustrator":
                self.current_image = message["content"]

        # innehåller bara ett svar från author. Why?
        print(response)
        # next_story = response.messages[0]["content"]
        # self.previous_story = next_story
        # return next_story

    # ===== Image generation ===== #
    async def _initialize_image_pipeline(self):
        await self.illustrator.initialize()

    async def _generate_image(self):
        print("Generating image..")
        if not self.current_story:
            raise ValueError(
                "No prompt(story) available for image generation"
            )

        image = await self.illustrator.generate_scene_image(
            description=self.current_story, width=512, height=768
        )

        if image:
            self.current_image = image
        else:
            print("Failed to generate image.")
