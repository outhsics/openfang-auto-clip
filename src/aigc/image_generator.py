"""
AI Image Generator for OpenFang Auto Clip.

Provides high-level interface for AI image generation.
"""

import os
import base64
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum

from .providers import AIProvider, get_provider, load_provider_config


class ImageStyle(Enum):
    """Predefined image generation styles"""

    REALISTIC = "realistic"
    ANIME = "anime"
    OIL_PAINTING = "oil_painting"
    WATERCOLOR = "watercolor"
    CYBERPUNK = "cyberpunk"
    FANTASY = "fantasy"
    MINIMALIST = "minimalist"
    VINTAGE = "vintage"
    POP_ART = "pop_art"
    CINEMATIC = "cinematic"


STYLE_PROMPTS = {
    ImageStyle.REALISTIC: "photorealistic, highly detailed, 8k resolution, professional photography",
    ImageStyle.ANIME: "anime style, studio ghibli, vibrant colors, clean lines",
    ImageStyle.OIL_PAINTING: "oil painting, classical art, textured brushstrokes",
    ImageStyle.WATERCOLOR: "watercolor painting, soft colors, artistic, delicate",
    ImageStyle.CYBERPUNK: "cyberpunk, neon lights, futuristic, sci-fi, high contrast",
    ImageStyle.FANTASY: "fantasy art, magical, ethereal, mystical atmosphere",
    ImageStyle.MINIMALIST: "minimalist, clean, simple, modern aesthetic",
    ImageStyle.VINTAGE: "vintage, retro, nostalgic, film grain, aged",
    ImageStyle.POP_ART: "pop art, bold colors, comic book style, vibrant",
    ImageStyle.CINEMATIC: "cinematic, movie scene, dramatic lighting, film still",
}


class ImageGenerator:
    """AI Image Generator"""

    def __init__(
        self,
        provider: Optional[AIProvider] = None,
        output_dir: Optional[Path] = None
    ):
        """
        Initialize image generator

        Args:
            provider: AI provider to use (auto-detected if None)
            output_dir: Output directory for generated images
        """
        if provider is None:
            config = load_provider_config()
            default_provider = config.get("default_provider", "stable_diffusion")
            provider_config = config.get("providers", {}).get(default_provider, {})
            provider = get_provider(
                default_provider,
                api_key=provider_config.get("api_key"),
                base_url=provider_config.get("base_url")
            )

        self.provider = provider
        self.output_dir = output_dir or Path.home() / ".openfang" / "aigc" / "images"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._generation_history: List[Dict] = []

    def generate(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        style: Optional[ImageStyle] = None,
        width: int = 1024,
        height: int = 1024,
        steps: int = 20,
        guidance_scale: float = 7.5,
        seed: int = -1,
        save_path: Optional[Path] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate image from prompt

        Args:
            prompt: Text description of desired image
            negative_prompt: Things to avoid in the image
            style: Predefined style to apply
            width: Image width
            height: Image height
            steps: Number of generation steps
            guidance_scale: How strongly to follow the prompt
            seed: Random seed (-1 for random)
            save_path: Where to save the image (auto-generated if None)
            **kwargs: Additional provider-specific parameters

        Returns:
            Dictionary with generation result
        """
        # Apply style if specified
        if style:
            style_suffix = STYLE_PROMPTS.get(style, "")
            prompt = f"{prompt}, {style_suffix}"

        # Generate image
        result = self.provider.generate_image(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            steps=steps,
            guidance_scale=guidance_scale,
            seed=seed,
            **kwargs
        )

        # Save image if successful
        if result.get("success"):
            save_path = save_path or self._generate_save_path()
            self._save_image(result, save_path)
            result["save_path"] = str(save_path)

            # Record in history
            self._generation_history.append({
                "timestamp": datetime.now().isoformat(),
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "style": style.value if style else None,
                "width": width,
                "height": height,
                "save_path": str(save_path),
                "provider": self.provider.provider_type.value,
                "success": True
            })

        return result

    def generate_batch(
        self,
        prompts: List[str],
        negative_prompt: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple images

        Args:
            prompts: List of text prompts
            negative_prompt: Common negative prompt for all images
            **kwargs: Additional parameters passed to generate()

        Returns:
            List of generation results
        """
        results = []
        for i, prompt in enumerate(prompts):
            print(f"Generating image {i+1}/{len(prompts)}: {prompt[:50]}...")
            result = self.generate(prompt, negative_prompt, **kwargs)
            results.append(result)

        return results

    def generate_variations(
        self,
        base_prompt: str,
        num_variations: int = 4,
        variation_strength: float = 0.3,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Generate variations of a base prompt

        Args:
            base_prompt: Base prompt to vary
            num_variations: Number of variations to generate
            variation_strength: How much to vary (0.0-1.0)
            **kwargs: Additional parameters

        Returns:
            List of generation results
        """
        variation_suffixes = [
            "with dramatic lighting",
            "from a different angle",
            "with vibrant colors",
            "in a different style",
            "with detailed background",
            "close-up view",
            "wide angle view",
            "with soft focus",
        ]

        results = []
        for i in range(num_variations):
            # Add variation to prompt
            if i < len(variation_suffixes):
                prompt = f"{base_prompt}, {variation_suffixes[i]}"
            else:
                prompt = base_prompt

            # Vary seed for different results
            kwargs["seed"] = -1  # Random seed

            result = self.generate(prompt, **kwargs)
            results.append(result)

        return results

    def img2img(
        self,
        input_image: Path,
        prompt: str,
        negative_prompt: Optional[str] = None,
        denoising_strength: float = 0.75,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Transform an existing image

        Args:
            input_image: Path to input image
            prompt: How to transform the image
            negative_prompt: Things to avoid
            denoising_strength: How much to transform (0.0-1.0)
            **kwargs: Additional parameters

        Returns:
            Generation result
        """
        # This requires img2img support from the provider
        # For now, we'll return a not-implemented response
        return {
            "success": False,
            "error": "img2img requires provider-specific implementation",
            "note": "Use ComfyUI or Stable Diffusion WebUI for img2img"
        }

    def upscale(
        self,
        input_image: Path,
        scale_factor: float = 2.0,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Upscale an image

        Args:
            input_image: Path to input image
            scale_factor: How much to upscale (1.5, 2.0, 4.0)
            **kwargs: Additional parameters

        Returns:
            Generation result
        """
        return {
            "success": False,
            "error": "Upscaling requires provider-specific implementation",
            "note": "Use ESRGAN or Real-ESRGAN for upscaling"
        }

    def _generate_save_path(self) -> Path:
        """Generate unique save path for image"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"generated_{timestamp}.png"
        return self.output_dir / filename

    def _save_image(self, result: Dict[str, Any], save_path: Path):
        """Save image from result to disk"""
        if "image_base64" in result:
            # Decode base64 and save
            image_data = base64.b64decode(result["image_base64"])
            with open(save_path, "wb") as f:
                f.write(image_data)

        elif "image_url" in result:
            # Download from URL
            response = requests.get(result["image_url"], timeout=30)
            response.raise_for_status()
            with open(save_path, "wb") as f:
                f.write(response.content)

    def get_history(self, limit: int = 10) -> List[Dict]:
        """Get recent generation history"""
        return self._generation_history[-limit:]

    def clear_history(self):
        """Clear generation history"""
        self._generation_history.clear()


def generate_image(
    prompt: str,
    provider: str = "stable_diffusion",
    style: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function to generate an image

    Args:
        prompt: Text description
        provider: AI provider to use
        style: Style to apply (realistic, anime, etc.)
        **kwargs: Additional parameters

    Returns:
        Generation result
    """
    # Convert style string to enum
    image_style = None
    if style:
        try:
            image_style = ImageStyle(style.lower())
        except ValueError:
            print(f"⚠️  Unknown style: {style}. Using default.")

    # Create generator
    generator = ImageGenerator(provider=get_provider(provider))

    # Generate
    return generator.generate(prompt, style=image_style, **kwargs)


# Preset prompts for common use cases
PRESET_PROMPTS = {
    "youtube_thumbnail": {
        "prompt": "Professional YouTube thumbnail, eye-catching, bold text, high contrast, 4k quality",
        "width": 1280,
        "height": 720
    },
    "video_background": {
        "prompt": "Abstract background, gradient, modern, clean, suitable for video backdrop",
        "width": 1920,
        "height": 1080
    },
    "social_media_post": {
        "prompt": "Social media post, engaging, aesthetic, Instagram-worthy",
        "width": 1080,
        "height": 1080
    },
    "character_design": {
        "prompt": "Character design, full body, detailed, expressive, professional art",
        "width": 1024,
        "height": 1536
    },
    "landscape": {
        "prompt": "Beautiful landscape, scenic, natural lighting, highly detailed",
        "width": 1920,
        "height": 1080
    },
}


def generate_preset(preset_name: str, customizations: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Generate image using preset configuration

    Args:
        preset_name: Name of preset
        customizations: Optional customizations to override preset

    Returns:
        Generation result
    """
    if preset_name not in PRESET_PROMPTS:
        return {
            "success": False,
            "error": f"Unknown preset: {preset_name}",
            "available_presets": list(PRESET_PROMPTS.keys())
        }

    preset = PRESET_PROMPTS[preset_name].copy()
    if customizations:
        preset.update(customizations)

    return generate_image(**preset)


if __name__ == "__main__":
    # Test image generation
    print("Testing AI Image Generator...")

    # Test with Stable Diffusion (if available)
    try:
        result = generate_image(
            prompt="A beautiful sunset over mountains",
            provider="stable_diffusion",
            width=1024,
            height=1024
        )

        if result.get("success"):
            print(f"✅ Image generated: {result.get('save_path')}")
        else:
            print(f"❌ Generation failed: {result.get('error')}")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure Stable Diffusion WebUI is running with --api flag")
