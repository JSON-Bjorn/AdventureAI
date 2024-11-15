from Swarm import Swarm, Agent


class SoundAgent:
    def __init__(self):
        self.client = Swarm()
        self.agent = Agent(
            name="The Narrator",
            model="TTS",
            instructions=(
                "You are a narrator for a story in a video game."
                "You will return soundfiles where you read from the inport text."
                "You analyze the context of the scene and adjust your voice accordingly."
                "You keep the listeners engaged with appropriate storytelling cadence."
            ),
        )
