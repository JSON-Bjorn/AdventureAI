import os
import sys
from swarm import Agent, Swarm
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Add project root to Python path
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.append(project_root)


class TextAgent:
    def __init__(self):
        load_dotenv()
        print("\n=== Initializing TextAgent ===")
        print("1. Setting up OpenAI client...")
        self.client = AsyncOpenAI()

        # Create Swarm agent
        self.agent = Agent(
            name="Story Generator",
            model="gpt-4",
            instructions="""You are a versatile storyteller for an interactive adventure game that adapts to ANY player choice.
Generate short, focused narratives (50 words max) that advance the story based on exactly what the player wants to do.

Key requirements:
1. Follow the player's lead completely - whether they seek epic adventures or simple moments
2. Match the tone and scale of the player's choice
3. Create appropriate consequences based on their actions
4. Keep descriptions grounded in the current situation
5. Return ONLY the story text, no meta commentary
6. Maintain consistency with the recent story history

If this is the first story (no previous context), create an engaging opening scene that sets up an adventure.

Remember: Return ONLY the story text. No explanations or meta text.""",
        )
        print("=== TextAgent initialization complete ===\n")

    async def generate_story(self, context: str) -> str:
        """Generate the next part of the story based on the given context."""
        try:
            print("\nDEBUG: Starting story generation")
            print("DEBUG: Context:", context)

            # Use Swarm client to run the agent
            swarm = Swarm()
            response = swarm.run(
                agent=self.agent,
                messages=[{"role": "user", "content": context}],
            )

            story = response.messages[-1]["content"].strip()
            print("DEBUG: Generated story:", story)
            return story
        except Exception as e:
            print("\nDEBUG: Error in generate_story")
            print(f"DEBUG: Error type: {type(e).__name__}")
            print(f"DEBUG: Error message: {str(e)}")
            import traceback

            print("DEBUG: Stack trace:")
            traceback.print_exc()
            raise
