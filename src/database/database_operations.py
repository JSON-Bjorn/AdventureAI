from typing import Dict


class DatabaseOperations:
    def __init__(self):
        pool = self.connection_pool()

    def save_game(self, context: Dict):
        # Post game save to db
        pass

    def load_game(self, game_id: str):
        # Get the game sve from db
        pass
