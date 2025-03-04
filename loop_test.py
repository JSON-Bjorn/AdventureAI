context = {
    "protagonist_name": "Felix",
    "inventory": ["Linux kernel, a glock 19"],
    "current_scene": {
        "story": "Current scene scene",
        "action": "Current action action",
    },
    "previous_scenes": [
        {
            "story": "This happens first",
            "action": "User chose this first",
        },
        {
            "story": "This happened second",
            "action": "User chose this second",
        },
        {
            "story": "This happened third",
            "action": "User chose this third",
        },
        {
            "story": "This happened fourth",
            "action": "User chose this fourth",
        },
    ],
}


def generate_story(context):
    """Builds the prompt and calls the mistral model for a new story"""

    instructions: str = "These are instructions"
    protagonist_name: str = context["protagonist_name"]
    inventory: str = ", ".join(context["inventory"])
    previous_scenes = context["previous_scenes"]
    current_scene = context["current_scene"]

    # Format the prompt
    formatted_prompt = f"""
Instructions: {instructions}

Protagonist: {protagonist_name}
Inventory: {inventory}

Previous scenes:
"""
    # Loop through previous scenes
    for i in range(10):
        try:
            formatted_prompt += f"Story: {previous_scenes[i]['story']}\n"
            formatted_prompt += (
                f"Action: {previous_scenes[i+1]['action']}\n\n"
            )
            formatted_prompt += f"Action successful: {previous_scenes[i+1]['action_success']}\n"
        except IndexError:
            break

    formatted_prompt += f"Action: {current_scene['action']}\n\n"
    formatted_prompt += (
        f"Action successful: {current_scene['action_success']}\n\n"
    )
    formatted_prompt += "Story: Next story goes here.\n"

    print(formatted_prompt)


generate_story(context)
