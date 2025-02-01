import os
import sys
from swarm import Swarm, Agent
from dotenv import load_dotenv
from random import randint

# Add project root to Python path
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.append(project_root)

load_dotenv()


class DiceRoller:
    def __init__(self):
        self.client = Swarm()
        self.agent = Agent(
            name="Dice master",
            model="gpt-4",
            instructions="""
You analyze the current story context and the player's intended action to determine if a difficulty check is needed and how difficult it should be.

First, determine if the action needs a roll at all. Many actions should automatically succeed:

NO ROLL NEEDED (Automatic Success) for:
- Basic movement (walking, sitting, standing)
- Simple observations (looking, listening)
- Basic social interactions (casual conversation)
- Common actions (opening unlocked doors, picking up items)
- Shopping or trading
- Resting or waiting
- Any mundane, everyday activity

Only require rolls for genuinely challenging actions:

Difficulty Guidelines when a roll IS needed:
5 (Very Easy):
- Simple physical tasks under pressure
- Basic persuasion of friendly NPCs
- Finding obvious clues

10 (Easy):
- Light athletics (climbing short walls, jumping gaps)
- Convincing reluctant but neutral NPCs
- Spotting well-hidden items
- Minor feats of skill

15 (Medium):
- Challenging physical feats
- Complex technical tasks
- Persuading hostile NPCs
- Combat with average opponents
- Dangerous environmental hazards

20 (Hard):
- Extremely difficult challenges
- Major feats of strength or skill
- Boss fights
- Life-threatening situations

Return ONLY a number:
0 = No roll needed (automatic success)
5 = Very Easy
10 = Easy  
15 = Medium
20 = Hard

No explanation, just the number.""",
        )

    def assess_situation(self, current_story, player_choice) -> int:
        """Determine if a roll is needed and how difficult it should be"""
        response = self.client.run(
            agent=self.agent,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Current scene: {current_story}\n"
                        f"Player wants to: {player_choice}"
                    ),
                }
            ],
        )

        try:
            dice_roll_needed = int(response.messages[0]["content"])
        except Exception:
            # Default to no roll needed if there's an error
            dice_roll_needed = 0

        return dice_roll_needed

    def roll_dice(self, dice_roll_needed) -> tuple[bool, int]:
        """Roll a d20 and determine success"""
        player_roll = randint(1, 20)

        # Critical failure on natural 1
        if player_roll == 1:
            success = False
        # Critical success on natural 20
        elif player_roll == 20:
            success = True
        # Otherwise check against difficulty
        else:
            success = player_roll >= dice_roll_needed

        return (success, player_roll)
