from swarm import Swarm, Agent
from dotenv import load_dotenv
from random import randint

load_dotenv()


class DiceRoller:
    def __init__(self):
        self.client = Swarm()
        self.agent = Agent(
            name="Dice master funk flex 3000",
            model="gpt-4",
            instructions=(
                "You are a master of determining the difficulty of tasks set "
                "in a dungeons and dragons type-video game. "
                "You analyze the current story context and the player's intended action "
                "to determine an appropriate difficulty check.\n\n"
                "Difficulty Guidelines:\n"
                "0: Automatic success, no roll needed (looking, thinking, simple movement)\n"
                "5: Very Easy (finding water in a forest, opening an unlocked door)\n"
                "10: Easy (climbing a short wall, convincing a friendly NPC)\n"
                "15: Medium (fighting average enemies, complex physical tasks)\n"
                "20: Hard (very difficult challenges, boss fights)\n\n"
                "Consider:\n"
                "- Context of the story\n"
                "- Physical vs mental tasks\n"
                "- Environmental factors\n"
                "- Risk level\n\n"
                "Return only a number from: [0,5,10,15,20]\n"
                "No letters, no symbols, just the number."
            ),
        )

    def assess_situation(self, current_story, player_choice) -> int:
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
            dice_roll_needed = 10

        return dice_roll_needed

    def roll_dice(self, dice_roll_needed) -> bool:
        player_roll = randint(1, 20)

        if player_roll == 1:
            success = False
        elif player_roll >= dice_roll_needed or player_roll == 20:
            success = True
        else:
            success = False

        return (success, player_roll)
