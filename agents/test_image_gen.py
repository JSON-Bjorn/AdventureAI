import asyncio
from illustrator_agent import IllustratorAgent


async def test_image_generation():
    # Create an instance of the IllustratorAgent
    agent = IllustratorAgent()

    # Initialize the pipeline
    print("Initializing the agent...")
    await agent.initialize()

    try:
        # Test scene generation with different prompts
        test_scenes = [
            "A majestic castle on a hilltop during sunset, with dragons flying in the distance",
            "A mystical forest clearing with glowing mushrooms and fireflies at night",
            "An ancient temple ruins in a jungle, rays of sunlight breaking through the canopy",
        ]

        for i, scene_description in enumerate(test_scenes, 1):
            print(f"\nGenerating test image {i}...")
            print(f"Prompt: {scene_description}")

            # Generate the image
            image = await agent.generate_scene_image(
                description=scene_description,
                width=512,  # You can adjust width/height as needed
                height=748,
            )

            if image:
                # Save the generated image
                output_path = f"test_scene_{i}.png"
                image.save(output_path)
                print(f"Image saved successfully to: {output_path}")
            else:
                print("Failed to generate image")

    finally:
        # Clean up resources
        await agent.cleanup()
        print("\nCleanup completed")


if __name__ == "__main__":
    # Run the test
    asyncio.run(test_image_generation())
