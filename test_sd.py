"""
Simulates image generation in the game loop.
Opens up the image in a new window.
"""

from src.generative_apis import ImageGeneration
from PIL import Image
import asyncio
import base64
from io import BytesIO


async def main():
    prompt = "A knight in blue armor holding a gigantic axe, standing in a cow pen, cows in the background, cinematic lighting, detailed shading, high resolution, detailed background and foreground elements"
    image_generator = ImageGeneration()
    base64_image = await image_generator.stable_diffusion_call(prompt)
    image_data = BytesIO(base64.b64decode(base64_image))
    image = Image.open(image_data)
    image.show()


if __name__ == "__main__":
    asyncio.run(main())
