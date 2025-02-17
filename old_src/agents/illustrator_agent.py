import os
from typing import Optional, Dict
from PIL import Image
import logging
import torch
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
from dotenv import load_dotenv


class IllustratorAgent:
    """Agent responsible for generating images for scenes and characters."""

    def __init__(self):
        super().__init__()
        # Force reload environment variables
        load_dotenv(override=True)

        self.models_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "models",
        )
        # Add debug print to verify the model name
        model_name = os.getenv("IMAGE_MODEL")
        print(f"Loading model: {model_name}")

        self.model_file = model_name + ".safetensors"
        self.pipeline = None
        self.max_tokens = 77  # CLIP token limit
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self._is_initialized = False

        # Configure CUDA settings
        if torch.cuda.is_available():
            torch.backends.cuda.matmul.allow_tf32 = (
                True  # Better performance on RTX 30 series
            )
            torch.backends.cudnn.allow_tf32 = True
            self.device = "cuda"

            # Print GPU diagnostics
            print("\nGPU Diagnostics:")
            print(f"CUDA available: {torch.cuda.is_available()}")
            print(f"CUDA version: {torch.version.cuda}")
            print(f"GPU device: {torch.cuda.get_device_name(0)}")
            print(
                f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB"
            )
        else:
            print("No CUDA GPU detected. Please check:")
            print("1. NVIDIA drivers are up to date")
            print("2. PyTorch is installed with CUDA support")
            print("3. CUDA toolkit is installed")
            self.device = "cpu"
            raise RuntimeError("CUDA GPU required for image generation")

        # This should be a reference to where we give the image prompts.
        self.agent = None

        # Add configuration parameters for better control
        self.default_config = {
            "num_inference_steps": 4,
            "guidance_scale": 2.0,
            "negative_prompt": """text, watermark, logo, title, signature, blurry, 
                low quality, distorted, deformed, disfigured, bad anatomy, 
                out of frame, extra limbs, duplicate, meme, cartoon, anime""",
        }

        # Category-specific enhancement keywords
        self.category_enhancements = {
            "person": [
                "detailed facial features",
                "realistic skin texture",
                "natural pose",
                "expressive eyes",
                "detailed clothing folds",
                "anatomically correct",
            ],
            "landscape": [
                "atmospheric perspective",
                "detailed foliage",
                "natural lighting",
                "environmental storytelling",
                "realistic textures",
                "depth of field",
            ],
            "building": [
                "architectural details",
                "realistic materials",
                "proper perspective",
                "structural integrity",
                "weathering effects",
            ],
            "interior": [
                "ambient occlusion",
                "realistic lighting",
                "detailed furnishings",
                "proper perspective",
                "atmospheric depth",
            ],
            "object": [
                "fine details",
                "realistic materials",
                "proper scale",
                "surface texturing",
                "realistic reflections",
            ],
            "creature": [
                "anatomically plausible",
                "detailed scales/fur/skin",
                "realistic eyes",
                "natural pose",
                "proper proportions",
            ],
        }

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
        if self._is_initialized:
            print("Illustrator already initialized, skipping...")
            return

        try:
            print("\n=== Initializing IllustratorAgent ===")
            print(f"1. Device configuration: {self.device}")
            print("2. Memory status before initialization:")
            if torch.cuda.is_available():
                print(
                    f"- CUDA memory allocated: {torch.cuda.memory_allocated(0) / 1024**2:.2f} MB"
                )
                print(
                    f"- CUDA memory cached: {torch.cuda.memory_reserved(0) / 1024**2:.2f} MB"
                )

            # Clear CUDA cache before loading model
            if torch.cuda.is_available():
                print("3. Clearing CUDA cache...")
                torch.cuda.empty_cache()

            model_path = os.path.join(self.models_dir, self.model_file)
            print(f"4. Checking model path: {model_path}")
            if not os.path.exists(model_path):
                print(f"Error: Model not found at {model_path}")
                print(
                    f"Please ensure the model file '{self.model_file}' is in the models directory"
                )
                print(f"Current directory structure:")
                print(
                    f"- Models dir exists: {os.path.exists(self.models_dir)}"
                )
                print(
                    f"- Contents of models dir: {os.listdir(self.models_dir) if os.path.exists(self.models_dir) else 'N/A'}"
                )
                raise FileNotFoundError(f"Model not found at {model_path}")

            print("5. Loading pipeline...")
            try:
                self.pipeline = StableDiffusionXLPipeline.from_single_file(
                    model_path,
                    torch_dtype=torch.float16,
                    use_safetensors=True,
                    variant="fp16",
                )
                print("6. Pipeline loaded successfully")
            except Exception as e:
                print(f"Error loading pipeline: {str(e)}")
                raise

            print("7. Moving pipeline to device and optimizing...")
            try:
                self.pipeline.to(self.device)
                self.pipeline.enable_attention_slicing(slice_size="max")
                self.pipeline.enable_vae_tiling()
                self.pipeline.enable_model_cpu_offload()
                print("8. Pipeline optimization complete")
            except Exception as e:
                print(f"Error during pipeline optimization: {str(e)}")
                raise

            try:
                print("9. Enabling xformers...")
                self.pipeline.enable_xformers_memory_efficient_attention()
                print("10. Xformers enabled successfully")
            except Exception as e:
                print(f"Note: Xformers not available: {e}")

            self._is_initialized = True
            print("\n=== IllustratorAgent initialization complete ===")
            print("Final memory status:")
            if torch.cuda.is_available():
                print(
                    f"- CUDA memory allocated: {torch.cuda.memory_allocated(0) / 1024**2:.2f} MB"
                )
                print(
                    f"- CUDA memory cached: {torch.cuda.memory_reserved(0) / 1024**2:.2f} MB\n"
                )

        except Exception as e:
            print(f"\n=== Error in IllustratorAgent initialization ===")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            import traceback

            traceback.print_exc()
            # Clean up if initialization fails
            await self.cleanup()
            raise

    async def cleanup(self):
        """Clean up resources."""
        if self.pipeline is not None:
            try:
                self.pipeline.to("cpu")  # Move to CPU first
                del self.pipeline
                self.pipeline = None
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()  # Clear CUDA cache
                self._is_initialized = False
            except Exception as e:
                self.log_error("Error during cleanup", e)

    async def reset_state(self):
        """Reset the agent's state without reinitializing the pipeline"""
        if not self._is_initialized:
            await self.initialize()
        else:
            # Clear any temporary memory
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

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
        prompt: str,
        width: int = 768,
        height: int = 768,
        **kwargs,
    ) -> Optional[Image.Image]:
        """Generate an image based on the provided prompt"""
        if not self._is_initialized:
            await self.initialize()

        try:
            if torch.cuda.is_available():
                # Clear cache before generation
                torch.cuda.empty_cache()

            # Extract prompt and negative_prompt if provided as dict
            if isinstance(prompt, dict):
                negative_prompt = prompt.get(
                    "negative_prompt", self.default_config["negative_prompt"]
                )
                prompt = prompt["prompt"]
            else:
                negative_prompt = self.default_config["negative_prompt"]

            # Allow override of default config via kwargs
            config = {**self.default_config, **kwargs}
            config["negative_prompt"] = negative_prompt

            # Truncate prompt if needed
            truncated_prompt = self._truncate_prompt(prompt)

            # Generate with error handling and progress callback
            return await self._generate_with_fallback(
                truncated_prompt, width, height, config
            )

        except Exception as e:
            self.log_error("Error generating scene image", e)
            return None

    async def _generate_with_fallback(self, prompt, width, height, config):
        """Attempt generation with fallback to safer settings if needed"""
        try:
            # First attempt with optimal settings
            return await self._generate_image(prompt, width, height, config)
        except RuntimeError as e:
            if "out of memory" in str(e):
                # Fallback to lower memory settings
                self.log_info("Falling back to low-memory settings...")
                config["num_inference_steps"] = max(
                    2, config["num_inference_steps"] - 2
                )
                torch.cuda.empty_cache()
                return await self._generate_image(
                    prompt, width, height, config
                )
            raise

    async def _generate_image(self, prompt, width, height, config):
        """Core image generation logic"""
        generator = torch.Generator(device=self.device).manual_seed(
            int(torch.randint(0, 2**32 - 1, (1,)).item())
        )

        with torch.inference_mode():
            image = self.pipeline(
                prompt=prompt,
                negative_prompt=config["negative_prompt"],
                width=width,
                height=height,
                num_inference_steps=config["num_inference_steps"],
                guidance_scale=config["guidance_scale"],
                num_images_per_prompt=1,
                generator=generator,
                output_type="pil",
            ).images[0]

        return image

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
