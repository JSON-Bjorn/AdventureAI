import pygame
import textwrap
from PIL import Image
import io
import numpy as np


class DisplayManager:
    def __init__(self, width=1024, height=768):
        # Initialize pygame and its modules
        pygame.init()
        pygame.font.init()

        # Initialize mixer with specific settings for better compatibility
        pygame.mixer.init(
            frequency=44100,  # Standard frequency
            size=-16,  # 16-bit audio
            channels=2,  # Stereo
            buffer=2048,  # Buffer size
        )

        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("AdventureAI")

        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (100, 100, 100)

        # Fonts
        self.story_font = pygame.font.SysFont("Arial", 24)
        self.input_font = pygame.font.SysFont("Arial", 20)

        # Text input
        self.input_text = ""
        self.input_rect = pygame.Rect(10, height - 40, width - 20, 30)

        # Calculate dimensions for square image display
        image_size = height - 60  # Square image height/width

        # Story display area (adjust to fill remaining width)
        story_width = width - image_size - 30  # 30 for padding
        self.story_rect = pygame.Rect(10, 10, story_width, height - 60)

        # Image display area (fixed to 768x768)
        self.image_rect = pygame.Rect(
            width - image_size - 10,  # 10px padding from right
            10,  # 10px padding from top
            image_size,  # Square width
            image_size,  # Square height
        )

        self.current_story = ""
        self.current_image = None

    def pil_image_to_surface(self, pil_image):
        """Convert PIL image to Pygame surface"""
        if pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")

        # Resize image to exactly match our square display area
        new_size = self.image_rect.width  # Square size

        pil_image = pil_image.resize(
            (new_size, new_size), Image.Resampling.LANCZOS
        )

        image_data = pil_image.tobytes()
        pygame_image = pygame.image.fromstring(
            image_data, pil_image.size, pil_image.mode
        )
        return pygame_image

    def update_story(self, text):
        """Update the story text"""
        self.current_story = text  # Simply replace existing text

    def update_image(self, pil_image):
        """Update the displayed image"""
        if pil_image:
            self.current_image = self.pil_image_to_surface(pil_image)

    def render(self):
        """Render everything to the screen"""
        self.screen.fill(self.BLACK)

        # Draw story area background
        pygame.draw.rect(self.screen, self.GRAY, self.story_rect, 2)

        # Calculate max characters per line based on font size and story rect width
        font_width = self.story_font.size("A")[
            0
        ]  # Get average character width
        chars_per_line = (
            self.story_rect.width - 20
        ) // font_width  # -20 for padding

        # Render story text with improved word wrap
        wrapped_text = textwrap.fill(self.current_story, width=chars_per_line)
        y_offset = self.story_rect.top + 10

        # Handle text scrolling if it exceeds the box height
        lines = wrapped_text.split("\n")
        visible_lines = (
            self.story_rect.height - 20
        ) // self.story_font.get_height()
        lines = lines[-visible_lines:]  # Only show last N lines that fit

        for line in lines:
            text_surface = self.story_font.render(line, True, self.WHITE)
            # Ensure text stays within bounds
            if (
                y_offset + self.story_font.get_height()
                <= self.story_rect.bottom - 10
            ):
                self.screen.blit(
                    text_surface, (self.story_rect.left + 10, y_offset)
                )
                y_offset += self.story_font.get_height()

        # Draw image area
        pygame.draw.rect(self.screen, self.GRAY, self.image_rect, 2)
        if self.current_image:
            # Center the image in the image rect
            image_x = (
                self.image_rect.centerx - self.current_image.get_width() // 2
            )
            image_y = (
                self.image_rect.centery - self.current_image.get_height() // 2
            )
            self.screen.blit(self.current_image, (image_x, image_y))

        # Draw input area
        pygame.draw.rect(self.screen, self.WHITE, self.input_rect, 2)
        text_surface = self.input_font.render(
            self.input_text, True, self.WHITE
        )
        self.screen.blit(
            text_surface, (self.input_rect.x + 5, self.input_rect.y + 5)
        )

        pygame.display.flip()

    def handle_input(self, event):
        """Handle text input events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                input_value = self.input_text
                self.input_text = ""
                return input_value
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            else:
                self.input_text += event.unicode
        return None
