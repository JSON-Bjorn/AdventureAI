"""
Quickstart script for AdventureAI - Launches the game directly without dependency checks
"""

import sys
import os
import asyncio

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from src.adventureai import instantialize_agents

if __name__ == "__main__":
    try:
        # Set up asyncio event loop policy for Windows
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(
                asyncio.WindowsSelectorEventLoopPolicy()
            )

        print("QuickStart: Launching AdventureAI...")
        asyncio.run(instantialize_agents())

    except Exception as e:
        print("\nError during quickstart:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")

        # Keep window open if there was an error
        if sys.exc_info()[0] is not None:
            input("\nPress Enter to exit...")

    finally:
        print("\nExiting...")
        sys.exit()
