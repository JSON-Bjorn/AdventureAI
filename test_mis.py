from src.api.generative_apis import TextGeneration
import asyncio


async def simulated_game_loop(context):
    text_gen = TextGeneration()
    test_story = await text_gen.generate_story(context)
    print("API RESPONSE:\n")
    print(test_story)


if __name__ == "__main__":
    context = {
        "protagonist_name": "Linus Torvalds",
        "inventory": ["Materialized Linux kernel"],
        "current_scene": {
            "story": "You sit down on the toiled seat, its warm.",
            "action": "I roll up a joint and start smoking.",
            "dice_threshhold": None,
            "dice_success": None,
        },
        "previous_scenes": [
            {
                "story": "You are Walking down the street.",
                "action": "I go into a cafe and order a coffee.",
                "dice_threshhold": 20,
                "dice_success": True,
            },
            {
                "story": "You are sitting in a cafe, drinking a coffee.",
                "action": "I go to the bathroom.",
                "dice_threshhold": 20,
                "dice_success": True,
            },
        ],
        "mood": {
            1: "calm",
            2: "adventerous",
        },
    }

    asyncio.run(simulated_game_loop(context))
