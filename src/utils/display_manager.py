import pygame
import textwrap
from PIL import Image
import io
import numpy as np
import os
import json
import time


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

        # Load last window position
        self.config_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "config",
            "window_position.json",
        )
        window_pos = self.load_window_position()

        if window_pos:
            os.environ["SDL_VIDEO_WINDOW_POS"] = (
                f"{window_pos['x']},{window_pos['y']}"
            )

        self.screen = pygame.display.set_mode(
            (width, height),
            pygame.RESIZABLE | pygame.SHOWN,
        )
        pygame.display.set_caption("AdventureAI")

        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (100, 100, 100)

        # Fonts
        self.story_font = pygame.font.SysFont("Arial", 48)
        self.input_font = pygame.font.SysFont("Arial", 40)

        # Fixed dimensions
        self.text_width = 768  # Width for text area
        self.image_size = 768  # Size for square image

        # Calculate remaining height for input
        remaining_height = height - self.image_size - 30  # 30px for margins
        input_height = remaining_height

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
            input_height,  # Use all remaining height
        )

        # Add dice button (under the image area, slightly larger)
        button_size = int(input_height * 1.2)  # 20% larger than before
        self.dice_button_rect = pygame.Rect(
            self.text_width + 30,  # Same x position as image
            self.image_size + 20,  # Same y position as input field
            button_size,  # Square button
            button_size,
        )

        # Create dice icon
        self.dice_icon = self._create_dice_icon(button_size)

        # Add dice button colors
        self.DICE_INACTIVE = (30, 30, 30)  # Very dark gray when inactive
        self.DICE_ACTIVE = (50, 50, 50)  # Slightly lighter when active
        self.DICE_HOVER = self.GRAY  # Full gray on hover when active

        # Add dice button state
        self.dice_button_active = (
            False  # Controls functionality, not visibility
        )
        self.dice_button_hover = False

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

        # Add placeholder text
        self.placeholder_text = "Type your next action here..."
        self.input_active = False

        # Add key repeat for holding down keys
        pygame.key.set_repeat(
            300, 50
        )  # 300ms initial delay, 50ms repeat interval

        # Add close button
        self.close_button_rect = pygame.Rect(width - 40, 0, 40, 40)

        # Add loading status
        self.loading_status = ""
        self.loading_font = pygame.font.SysFont("Arial", 12)
        self.loading_color = (150, 150, 150)  # Light gray

    def load_window_position(self):
        """Load the last window position from config file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading window position: {e}")
        return None

    def save_window_position(self):
        """Save the current window position to config file"""
        try:
            # Get current window position
            x, y = pygame.display.get_window_position()

            # Ensure config directory exists
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)

            # Save position
            with open(self.config_file, "w") as f:
                json.dump({"x": x, "y": y}, f)
        except Exception as e:
            print(f"Error saving window position: {e}")

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

    def set_loading_status(self, status: str):
        """Update the loading status text"""
        self.loading_status = status

    def _create_dice_icon(self, size):
        """Create a D20 (20-sided die) icon based on standard D&D design"""
        padding = 4
        icon_surface = pygame.Surface((size, size), pygame.SRCALPHA)

        # Calculate center and points
        center = (size // 2, size // 2)
        radius = (size - padding * 2) // 2

        # Create hexagon points for the main shape
        hexagon_points = []
        for i in range(6):
            angle = i * (2 * 3.14159 / 6)  # Divide circle into 6 parts
            x = center[0] + int(radius * np.cos(angle))
            y = center[1] + int(radius * np.sin(angle))
            hexagon_points.append((x, y))

        # Draw the main hexagonal shape (white fill)
        pygame.draw.polygon(icon_surface, self.WHITE, hexagon_points)

        # Draw the internal lines to create the D20 face pattern
        # Vertical center line
        pygame.draw.line(
            icon_surface,
            self.BLACK,
            (center[0], center[1] - radius),
            (center[0], center[1] + radius),
            2,
        )

        # Draw diagonal lines
        left_point = (
            center[0] - int(radius * 0.866),
            center[1],
        )  # cos(60°) ≈ 0.866
        right_point = (center[0] + int(radius * 0.866), center[1])
        top_point = (center[0], center[1] - radius)
        bottom_point = (center[0], center[1] + radius)

        # Main triangular sections
        pygame.draw.line(icon_surface, self.BLACK, left_point, right_point, 2)
        pygame.draw.line(icon_surface, self.BLACK, left_point, top_point, 2)
        pygame.draw.line(icon_surface, self.BLACK, right_point, top_point, 2)
        pygame.draw.line(
            icon_surface, self.BLACK, left_point, bottom_point, 2
        )
        pygame.draw.line(
            icon_surface, self.BLACK, right_point, bottom_point, 2
        )

        # Draw outline
        pygame.draw.polygon(icon_surface, self.BLACK, hexagon_points, 2)

        # Add the number "20" in the center
        font_size = size // 3
        number_font = pygame.font.SysFont("Arial", font_size, bold=True)
        number_surface = number_font.render("20", True, self.BLACK)
        number_rect = number_surface.get_rect(center=center)

        # Draw number
        icon_surface.blit(number_surface, number_rect)

        return icon_surface

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

        # Always draw dice button, but with different colors based on state
        if self.dice_button_active:
            button_color = (
                self.DICE_HOVER
                if self.dice_button_hover
                else self.DICE_ACTIVE
            )
        else:
            button_color = self.DICE_INACTIVE

        # Draw button background
        pygame.draw.rect(self.screen, button_color, self.dice_button_rect)
        pygame.draw.rect(self.screen, self.GRAY, self.dice_button_rect, 2)

        # Always draw dice icon, but slightly transparent when inactive
        icon_x = (
            self.dice_button_rect.centerx - self.dice_icon.get_width() // 2
        )
        icon_y = (
            self.dice_button_rect.centery - self.dice_icon.get_height() // 2
        )

        if not self.dice_button_active:
            # Create a dimmed version of the icon
            dimmed_icon = self.dice_icon.copy()
            dimmed_icon.set_alpha(128)  # 50% transparency
            self.screen.blit(dimmed_icon, (icon_x, icon_y))
        else:
            self.screen.blit(self.dice_icon, (icon_x, icon_y))

        # Render placeholder text if input is empty and not active
        if (
            not any(line for line in self.input_lines)
            and not self.input_active
        ):
            placeholder_surface = self.input_font.render(
                self.placeholder_text, True, self.GRAY
            )
            self.screen.blit(
                placeholder_surface,
                (self.input_rect.x + 10, self.input_rect.y + 5),
            )
        else:
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

        # Draw close button (X)
        pygame.draw.rect(self.screen, self.GRAY, self.close_button_rect, 2)
        # Draw X
        x_margin = 10
        pygame.draw.line(
            self.screen,
            self.WHITE,
            (
                self.close_button_rect.left + x_margin,
                self.close_button_rect.top + x_margin,
            ),
            (
                self.close_button_rect.right - x_margin,
                self.close_button_rect.bottom - x_margin,
            ),
            2,
        )
        pygame.draw.line(
            self.screen,
            self.WHITE,
            (
                self.close_button_rect.left + x_margin,
                self.close_button_rect.bottom - x_margin,
            ),
            (
                self.close_button_rect.right - x_margin,
                self.close_button_rect.top + x_margin,
            ),
            2,
        )

        # Render loading status in bottom right if there is a status
        if self.loading_status:
            loading_surface = self.loading_font.render(
                self.loading_status, True, self.loading_color
            )
            loading_rect = loading_surface.get_rect()
            # Position in bottom right with 20px margin
            loading_pos = (
                self.width - loading_rect.width - 20,
                self.height - loading_rect.height - 20,
            )
            self.screen.blit(loading_surface, loading_pos)

        pygame.display.flip()

    def handle_input(self, event):
        """Handle text input events with multi-line support"""
        if event.type == pygame.QUIT:
            # Save window position before quitting
            self.save_window_position()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Handle close button click
            if self.close_button_rect.collidepoint(event.pos):
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            # Handle dice button click - only return ROLL_DICE if active
            elif self.dice_button_rect.collidepoint(event.pos):
                if self.dice_button_active:
                    return "ROLL_DICE"
            # Handle input field focus
            elif self.input_rect.collidepoint(event.pos):
                self.input_active = True
            else:
                self.input_active = False

        elif event.type == pygame.MOUSEMOTION:
            # Update hover state only if button is active
            if self.dice_button_active:
                self.dice_button_hover = self.dice_button_rect.collidepoint(
                    event.pos
                )
            else:
                self.dice_button_hover = False

        elif event.type == pygame.KEYDOWN and self.input_active:
            if event.key == pygame.K_RETURN:
                # Join all lines and return the complete input
                input_value = "\n".join(self.input_lines)
                self.input_lines = [""]
                self.input_scroll = 0
                self.input_active = False
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
                # Add character to current line, checking width with larger font
                current_line = self.input_lines[-1] + event.unicode
                if (
                    self.input_font.size(current_line)[0]
                    > self.input_rect.width
                    - 40  # Increased margin for larger font
                ):
                    self.input_lines.append(event.unicode)
                    if len(self.input_lines) > 3:
                        self.input_scroll = len(self.input_lines) - 3
                else:
                    self.input_lines[-1] += event.unicode

        return None

    def render_loading(self, message: str):
        """Render a simple loading screen with message"""
        self.screen.fill(self.BLACK)

        # Render loading message using same style as in-game loading status
        loading_surface = self.loading_font.render(
            message, True, self.loading_color
        )
        loading_rect = loading_surface.get_rect()

        # Position in bottom right with 20px margin (same as in-game loading)
        loading_pos = (
            self.width - loading_rect.width - 20,
            self.height - loading_rect.height - 20,
        )

        # Draw message
        self.screen.blit(loading_surface, loading_pos)
        pygame.display.flip()  # Make sure to update the display

    def set_dice_button_active(self, active: bool):
        """Enable or disable the dice button"""
        self.dice_button_active = active
        self.dice_button_hover = False
