from new.agents import ImageAgent
from PIL import Image
import asyncio
import base64
from io import BytesIO

"""
This file is used to test the image generation API.
Make sure the server is running before running this file.
"""


async def main():
    prompt = "A knight in blue armor holding a gigantic axe, standing in a cow pen, cows in the background, cinematic lighting, detailed shading, high resolution, detailed background and foreground elements"
    image_agent = ImageAgent()
    base64_image = await image_agent.generate_image(prompt)
    image_data = BytesIO(base64.b64decode(base64_image))
    image = Image.open(image_data)
    image.show()


if __name__ == "__main__":
    asyncio.run(main())
