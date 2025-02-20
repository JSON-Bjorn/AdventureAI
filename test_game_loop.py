"""
Simulates the use of the Frontend API.
Initiates the game loop. Renders text in terminal and images in new windows.

"""

from src.game.game_loop import GameSession
import asyncio


async def main():
    game_session = GameSession(user_id="123", new_game=True)
    await game_session.game_loop()


if __name__ == "__main__":
    asyncio.run(main())
