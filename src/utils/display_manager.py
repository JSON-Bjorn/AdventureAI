import pygame
import textwrap
from PIL import Image
import io
import numpy as np
import os


class DisplayManager:
    def __init__(self, width=1600, height=960):
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
        os.environ["SDL_VIDEO_WINDOW_POS"] = "0,0"
        self.screen = pygame.display.set_mode((width, height), pygame.SHOWN)
        pygame.display.set_caption("AdventureAI")

        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (100, 100, 100)

        # Fonts
        self.story_font = pygame.font.SysFont("Arial", 24)
        self.input_font = pygame.font.SysFont("Arial", 20)

        # Fixed dimensions
        self.text_width = 768  # Width for text area
        self.image_size = 768  # Size for square image

        # Calculate remaining height for input
        remaining_height = height - self.image_size - 30  # 30px for margins

        # Story display area (same height as image)
        self.story_rect = pygame.Rect(
            10,  # x position
            10,  # y position
            self.text_width,  # Fixed width for text
            self.image_size,  # Same height as image
        )

        # Input field (uses remaining height)
        self.input_rect = pygame.Rect(
            10,  # x position
            self.image_size
            + 20,  # Position below story area with 10px margin
            self.text_width,  # Same width as story area
            remaining_height,  # Use all remaining height
        )

        # Image display area (fixed to 768x768)
        self.image_rect = pygame.Rect(
            self.text_width + 30,  # Position after text area plus margin
            10,  # 10px from top
            self.image_size,  # Exact image width
            self.image_size,  # Exact image height
        )

        # Text input state
        self.input_text = ""
        self.input_lines = [""]  # Track multiple lines
        self.input_scroll = 0  # Scroll position

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

        # Render story text with proper margins and wrapping
        story_width = self.story_rect.width - 20  # 10px margins on each side
        wrapped_lines = []
        words = self.current_story.split()
        current_line = []
        current_width = 0

        for word in words:
            word_surface = self.story_font.render(
                word + " ", True, self.WHITE
            )
            word_width = word_surface.get_width()

            if current_width + word_width > story_width:
                wrapped_lines.append(" ".join(current_line))
                current_line = [word]
                current_width = word_width
            else:
                current_line.append(word)
                current_width += word_width

        if current_line:
            wrapped_lines.append(" ".join(current_line))

        # Render story text
        y = self.story_rect.top + 10
        for line in wrapped_lines:
            if (
                y + self.story_font.get_height()
                <= self.story_rect.bottom - 10
            ):
                text_surface = self.story_font.render(line, True, self.WHITE)
                self.screen.blit(text_surface, (self.story_rect.left + 10, y))
                y += self.story_font.get_height()

        # Draw input area
        pygame.draw.rect(self.screen, self.GRAY, self.input_rect, 2)

        # Render input text with wrapping and scrolling
        visible_lines = min(6, len(self.input_lines) - self.input_scroll)
        for i in range(visible_lines):
            line_idx = i + self.input_scroll
            if line_idx < len(self.input_lines):
                text_surface = self.input_font.render(
                    self.input_lines[line_idx], True, self.WHITE
                )
                self.screen.blit(
                    text_surface,
                    (
                        self.input_rect.x + 10,
                        self.input_rect.y
                        + 5
                        + (i * self.input_font.get_height()),
                    ),
                )

        # Draw image area and image
        pygame.draw.rect(self.screen, self.GRAY, self.image_rect, 2)
        if self.current_image:
            image_x = (
                self.image_rect.centerx - self.current_image.get_width() // 2
            )
            image_y = (
                self.image_rect.centery - self.current_image.get_height() // 2
            )
            self.screen.blit(self.current_image, (image_x, image_y))

        pygame.display.flip()

    def handle_input(self, event):
        """Handle text input events with multi-line support"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # Join all lines and return the complete input
                input_value = "\n".join(self.input_lines)
                self.input_lines = [""]
                self.input_scroll = 0
                return input_value

            elif event.key == pygame.K_BACKSPACE:
                if self.input_lines[-1]:
                    self.input_lines[-1] = self.input_lines[-1][:-1]
                elif len(self.input_lines) > 1:
                    self.input_lines.pop()
                    self.input_scroll = max(0, len(self.input_lines) - 3)

            elif event.key == pygame.K_UP and self.input_scroll > 0:
                self.input_scroll -= 1

            elif (
                event.key == pygame.K_DOWN
                and self.input_scroll < len(self.input_lines) - 3
            ):
                self.input_scroll += 1

            else:
                # Add character to current line
                current_line = self.input_lines[-1] + event.unicode
                if (
                    self.input_font.size(current_line)[0]
                    > self.input_rect.width - 20
                ):
                    self.input_lines.append(event.unicode)
                    if len(self.input_lines) > 3:
                        self.input_scroll = len(self.input_lines) - 3
                else:
                    self.input_lines[-1] += event.unicode

        return None
