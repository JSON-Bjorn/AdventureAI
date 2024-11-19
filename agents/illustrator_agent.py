import os
from typing import Optional
from PIL import Image
import logging
import torch
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
from dotenv import load_dotenv


class IllustratorAgent:
    """Agent responsible for generating images for scenes and characters."""

    def __init__(self):
        super().__init__()
        load_dotenv()
        # Use a local model path from environment variables
        self.models_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "models",
        )
        self.model_file = os.getenv("IMAGE_MODEL") + ".safetensors"
        self.pipeline = None
        self.max_tokens = 77  # CLIP token limit
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # GPU diagnostics
        print("\nGPU Diagnostics:")
        print(f"CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"CUDA version: {torch.version.cuda}")
            print(f"GPU device: {torch.cuda.get_device_name(0)}")
            print(
                f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB"
            )
        else:
            print("No CUDA GPU detected. Please ensure you have:")
            print("1. A CUDA-capable GPU")
            print("2. NVIDIA drivers installed")
            print("3. PyTorch installed with CUDA support")

        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # This should be a reference to where we give the image prompts.
        # We could make it a Swarm agent. If we don't, we still call it agent for uniformity
        self.agent = None

    def log_error(
        self, message: str, error: Optional[Exception] = None
    ) -> None:
        """Log an error message."""
        if error:
            print(f"ERROR: {message} - {str(error)}")
        else:
            print(f"ERROR: {message}")

    def log_info(self, message: str) -> None:
        """Log an info message."""
        print(f"INFO: {message}")

    async def initialize(self):
        """Initialize the image generation pipeline."""
        try:
            print("Initializing image generation pipeline...")
            print(f"Using device: {self.device}")

            model_path = os.path.join(self.models_dir, self.model_file)
            if not os.path.exists(model_path):
                print(
                    f"Error: JuggernautXL Lightning model not found at {model_path}"
                )
                print(
                    f"Please ensure the model file '{self.model_file}' is in the models directory"
                )
                raise FileNotFoundError(f"Model not found at {model_path}")

            print(f"Loading JuggernautXL Lightning from: {model_path}")

            # Load the pipeline with optimized settings for Windows without Triton
            self.pipeline = StableDiffusionXLPipeline.from_single_file(
                model_path,
                torch_dtype=torch.float16
                if self.device == "cuda"
                else torch.float32,
                use_safetensors=True,
                variant="fp16",
            )
            self.pipeline.to(self.device)

            # Enable memory-efficient optimizations
            if self.device == "cuda":
                self.pipeline.enable_attention_slicing(
                    "max"
                )  # Maximum memory efficiency
                self.pipeline.enable_vae_tiling()  # Enable VAE tiling
                self.pipeline.enable_model_cpu_offload()  # Offload unused models to CPU

                # Use xformers if available
                try:
                    import xformers

                    self.pipeline.enable_xformers_memory_efficient_attention()
                    print("Enabled xformers memory efficient attention")
                except ImportError:
                    print("xformers not available, using default attention")

                # Use DPM++ 2M scheduler for fast inference
                self.pipeline.scheduler = (
                    DPMSolverMultistepScheduler.from_config(
                        self.pipeline.scheduler.config,
                        algorithm_type="dpmsolver++",
                        solver_order=2,
                    )
                )

            print("JuggernautXL Lightning pipeline initialized successfully!")
            self.log_info("Initialized JuggernautXL Lightning generator")

        except Exception as e:
            self.log_error("Failed to initialize image generator", e)
            raise

    async def cleanup(self):
        """Clean up resources."""
        if self.pipeline is not None:
            del self.pipeline
            torch.cuda.empty_cache()
            self.pipeline = None

    def _truncate_prompt(self, prompt: str) -> str:
        """Truncate prompt to stay within CLIP's token limit."""
        words = prompt.split()
        result = []
        current_length = 0

        for word in words:
            # Rough estimation: each word is ~1.5 tokens
            estimated_tokens = len(word.split()) * 1.5
            if (
                current_length + estimated_tokens > self.max_tokens - 2
            ):  # Leave room for special tokens
                break
            result.append(word)
            current_length += estimated_tokens

        return " ".join(result)

    def _enhance_scene_description(self, description: str) -> str:
        """Enhance scene description for better image generation."""
        # Extract key elements
        keywords = [
            "castle",
            "forest",
            "lake",
            "mountain",
            "cave",
            "village",
            "ruins",
            "temple",
            "bridge",
            "tower",
            "river",
            "valley",
            "city",
            "dungeon",
        ]

        # Add environmental details
        time_indicators = [
            "night",
            "day",
            "sunset",
            "sunrise",
            "dawn",
            "dusk",
        ]
        weather_conditions = [
            "rain",
            "storm",
            "clear sky",
            "cloudy",
            "misty",
            "foggy",
        ]

        # Check if scene has time of day
        has_time = any(
            time in description.lower() for time in time_indicators
        )
        has_weather = any(
            weather in description.lower() for weather in weather_conditions
        )

        # Build enhanced prompt
        enhanced = description.strip()

        # Add establishing shot indicator
        enhanced = "establishing shot, " + enhanced

        # Add time of day if missing
        if not has_time and "night" not in enhanced.lower():
            enhanced += ", daytime scene"

        # Add weather if missing
        if not has_weather:
            enhanced += ", clear atmosphere"

        return enhanced

    async def generate_scene_image(
        self,
        description: str,
        style: str = "epic fantasy art, detailed, cinematic, atmospheric",
        width: int = 512,
        height: int = 768,
    ) -> Optional[Image.Image]:
        """Generate an image for a scene based on the description."""
        try:
            # Clear CUDA cache before generation
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            # Generate random seed
            generator = torch.Generator(device=self.device).manual_seed(
                int(torch.randint(0, 2**32 - 1, (1,)).item())
            )

            # Enhance the description
            enhanced_description = self._enhance_scene_description(
                description
            )

            # Build high-quality prompt with specific details
            base_prompt = f"""masterpiece digital art, {enhanced_description}, {style}, 
                epic fantasy environment, volumetric lighting, dramatic composition, 
                detailed foreground and background elements, high detail landscape, 
                professional photography, artstation trending, award winning"""

            # Add negative prompt to avoid unwanted elements
            negative_prompt = """text, watermark, logo, title, signature, blurry, 
                low quality, distorted, deformed, disfigured, bad anatomy, 
                out of frame, extra limbs, duplicate, meme, cartoon, anime"""

            truncated_prompt = self._truncate_prompt(base_prompt)

            # Balanced generation settings for quality and speed
            with torch.inference_mode():
                image = self.pipeline(
                    prompt=truncated_prompt,
                    negative_prompt=negative_prompt,
                    width=width,
                    height=height,
                    num_inference_steps=4,  # Balanced speed and quality
                    guidance_scale=2.0,  # Moderate guidance for natural results
                    num_images_per_prompt=1,
                    generator=generator,
                    output_type="pil",
                ).images[0]

            return image

        except Exception as e:
            self.log_error("Error generating scene image", e)
            return None

    async def generate_character_image(
        self,
        description: str,
        style: str = "epic fantasy character art, detailed portrait, cinematic",
        width: int = 512,
        height: int = 768,
    ) -> Optional[Image.Image]:
        """Generate an image for a character based on the description."""
        try:
            # Clear CUDA cache before generation
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            # Generate random seed
            generator = torch.Generator(device=self.device).manual_seed(
                int(torch.randint(0, 2**32 - 1, (1,)).item())
            )

            # Build high-quality prompt with specific details
            base_prompt = f"""masterpiece digital art, detailed character portrait of {description}, 
                {style}, dynamic pose, expressive lighting, detailed facial features, 
                intricate costume details, professional character design, 
                artstation trending, award winning fantasy art"""

            # Add negative prompt
            negative_prompt = """text, watermark, logo, title, signature, blurry, 
                low quality, distorted, deformed, disfigured, bad anatomy, 
                out of frame, extra limbs, duplicate, meme, cartoon, anime"""

            truncated_prompt = self._truncate_prompt(base_prompt)

            # Balanced generation settings
            with torch.inference_mode():
                image = self.pipeline(
                    prompt=truncated_prompt,
                    negative_prompt=negative_prompt,
                    width=width,
                    height=height,
                    num_inference_steps=6,  # Balanced speed and quality
                    guidance_scale=2.0,  # Moderate guidance for natural results
                    num_images_per_prompt=1,
                    generator=generator,
                    output_type="pil",
                ).images[0]

            return image

        except Exception as e:
            self.log_error("Error generating character image", e)
            return None

    def save_image(self, image: Image.Image, filepath: str) -> bool:
        """Save the generated image to disk."""
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            image.save(filepath)
            self.log_info(f"Saved image to: {filepath}")
            return True
        except Exception as e:
            self.log_error(f"Error saving image to {filepath}", e)
            return False
