from swarm import Swarm, Agent
from dotenv import load_dotenv
from random import randint

load_dotenv()


class DiceRoller:
    def __init__(self):
        self.client = (
            Swarm()
        )  # Swarm will automatically use OPENAI_API_KEY from env
        self.agent = Agent(
            name="Dice master funk flex 3000",
            model="gpt-4",
            instructions=(
                "You are a master of determining the difficulty of tasks set"
                "in a dungeons and dragons type-video game."
                "You are going to reviece input in the form of a story that has been told "
                "along with a players choice of action in relation to that story."
                "Your job is to assess the difficulty of that action and return a number"
                "representing the difficulty."
                "For example: standing up, walking around, reaching for things are considered "
                "easy tasks and should have a difficulty of 0"
                "Tasks such as: swinging a sword, climbing a cliff, romancing someone are "
                "considered difficult and thus will have a higher difficulty."
                "The available difficulties are limited to:"
                "[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19 ,20]"
                "Always return only a number as your message. No letters, no symbols."
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
