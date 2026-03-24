"""
AI Provider Support for AIGC Integration.

Supports multiple AI providers for image and video generation.
"""

import os
import json
from typing import Dict, List, Optional, Any
from enum import Enum
from pathlib import Path
import requests


class ProviderType(Enum):
    """Supported AI provider types"""
    STABLE_DIFFUSION = "stable_diffusion"
    OPENAI_DALLE = "openai_dalle"
    MIDJOURNEY = "midjourney"
    REPLICATE = "replicate"
    HUGGINGFACE = "huggingface"
    COMFYUI = "comfyui"
    LIBLIB = "liblib"
    CUSTOM = "custom"


class AIProvider:
    """Base class for AI providers"""

    def __init__(
        self,
        provider_type: ProviderType,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        config: Optional[Dict] = None
    ):
        self.provider_type = provider_type
        self.api_key = api_key or os.getenv(f"{provider_type.value.upper()}_API_KEY")
        self.base_url = base_url
        self.config = config or {}
        self._validate_config()

    def _validate_config(self):
        """Validate provider configuration"""
        if not self.api_key and self.provider_type != ProviderType.CUSTOM:
            raise ValueError(f"API key required for {self.provider_type.value}")

    def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        width: int = 1024,
        height: int = 1024,
        steps: int = 20,
        guidance_scale: float = 7.5,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate image using this provider"""
        raise NotImplementedError("Subclasses must implement generate_image")

    def generate_video(
        self,
        prompt: str,
        duration: float = 4.0,
        fps: int = 30,
        width: int = 1024,
        height: int = 1024,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate video using this provider"""
        raise NotImplementedError("Subclasses must implement generate_video")

    def check_status(self) -> bool:
        """Check if provider is available"""
        try:
            response = requests.get(self._health_check_url(), timeout=5)
            return response.status_code == 200
        except:
            return False

    def _health_check_url(self) -> str:
        """Get health check URL for provider"""
        if self.base_url:
            return f"{self.base_url}/health"
        return ""


class StableDiffusionProvider(AIProvider):
    """Stable Diffusion provider (local or API)"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "http://127.0.0.1:7860",
        model: Optional[str] = None
    ):
        super().__init__(ProviderType.STABLE_DIFFUSION, api_key, base_url)
        self.model = model or "sd_xl_base_1.0"

    def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        width: int = 1024,
        height: int = 1024,
        steps: int = 20,
        guidance_scale: float = 7.5,
        seed: int = -1,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate image using Stable Diffusion"""
        url = f"{self.base_url}/sdapi/v1/txt2img"

        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt or "blurry, low quality, distorted",
            "width": width,
            "height": height,
            "steps": steps,
            "cfg_scale": guidance_scale,
            "seed": seed,
        }

        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=300)
            response.raise_for_status()
            result = response.json()

            return {
                "success": True,
                "image_base64": result.get("images", [])[0],
                "parameters": result.get("parameters", {}),
                "info": result.get("info", {})
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def generate_video(
        self,
        prompt: str,
        duration: float = 4.0,
        fps: int = 30,
        width: int = 1024,
        height: int = 1024,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate video using Stable Diffusion Video/Deforum"""
        # Check if video generation endpoint exists
        url = f"{self.base_url}/sdapi/v1/video2video"

        payload = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "video_length": int(duration * fps),
            "fps": fps,
        }

        try:
            response = requests.post(url, json=payload, timeout=600)
            response.raise_for_status()
            result = response.json()

            return {
                "success": True,
                "video_base64": result.get("video", ""),
                "info": result.get("info", {})
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "note": "Video generation requires Stable Diffusion Video or Deforum extension"
            }


class OpenAIDALLEProvider(AIProvider):
    """OpenAI DALL-E provider"""

    def __init__(self, api_key: Optional[str] = None):
        import openai
        super().__init__(ProviderType.OPENAI_DALLE, api_key or os.getenv("OPENAI_API_KEY"))
        self.client = openai.OpenAI(api_key=self.api_key)

    def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        width: int = 1024,
        height: int = 1024,
        model: str = "dall-e-3",
        quality: str = "standard",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate image using DALL-E"""
        try:
            # DALL-E 3 supports specific sizes
            size = f"{width}x{height}"
            if size not in ["1024x1024", "1792x1024", "1024x1792"]:
                size = "1024x1024"

            response = self.client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                quality=quality,
                n=1,
            )

            return {
                "success": True,
                "image_url": response.data[0].url,
                "revised_prompt": response.data[0].revised_prompt
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def generate_video(self, **kwargs) -> Dict[str, Any]:
        """DALL-E doesn't support video generation"""
        return {
            "success": False,
            "error": "DALL-E doesn't support video generation"
        }


class ReplicateProvider(AIProvider):
    """Replicate provider (supports multiple models)"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "stability-ai/sdxl"
    ):
        super().__init__(ProviderType.REPLICATE, api_key or os.getenv("REPLICATE_API_KEY"))
        self.model = model

    def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        width: int = 1024,
        height: int = 1024,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate image using Replicate"""
        try:
            import replicate

            output = replicate.run(
                self.model,
                input={
                    "prompt": prompt,
                    "negative_prompt": negative_prompt,
                    "width": width,
                    "height": height,
                }
            )

            return {
                "success": True,
                "image_url": output,
                "model": self.model
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def generate_video(
        self,
        prompt: str,
        duration: float = 4.0,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate video using Replicate"""
        try:
            import replicate

            video_model = "anotherjesse/zeroscope-v2-xl"  # or "stability-ai/stable-video-diffusion"

            output = replicate.run(
                video_model,
                input={
                    "prompt": prompt,
                    "num_frames": int(duration * 8),
                }
            )

            return {
                "success": True,
                "video_url": output,
                "model": video_model
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class LibLibProvider(AIProvider):
    """LibLib.tv provider (Chinese AI art platform)"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.liblib.art"
    ):
        super().__init__(ProviderType.LIBLIB, api_key, base_url)

    def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        model_id: Optional[str] = None,
        width: int = 1024,
        height: int = 1024,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate image using LibLib API"""
        url = f"{self.base_url}/v1/generate"

        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt or "",
            "model_id": model_id or "sd_xl",
            "width": width,
            "height": height,
        }

        headers = {"Authorization": f"Bearer {self.api_key}"}

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=300)
            response.raise_for_status()
            result = response.json()

            return {
                "success": True,
                "image_url": result.get("image_url"),
                "task_id": result.get("task_id")
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def generate_video(self, **kwargs) -> Dict[str, Any]:
        """LibLib video generation (if available)"""
        return {
            "success": False,
            "error": "Video generation not yet supported"
        }


class ComfyUIProvider(AIProvider):
    """ComfyUI provider (local node-based UI)"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "http://127.0.0.1:8188"
    ):
        super().__init__(ProviderType.COMFYUI, api_key, base_url)

    def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        workflow: Optional[Dict] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate image using ComfyUI workflow"""
        url = f"{self.base_url}/prompt"

        # Default workflow if none provided
        if not workflow:
            workflow = self._default_workflow(prompt, negative_prompt)

        payload = {
            "prompt": workflow,
            "client_id": "openfang_auto_clip"
        }

        try:
            response = requests.post(url, json=payload, timeout=300)
            response.raise_for_status()
            result = response.json()

            return {
                "success": True,
                "prompt_id": result.get("prompt_id"),
                "number": result.get("number"),
                "node_errors": result.get("node_errors", {})
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _default_workflow(self, prompt: str, negative_prompt: Optional[str]) -> Dict:
        """Generate default ComfyUI workflow"""
        return {
            "1": {
                "class_type": "KSampler",
                "inputs": {
                    "seed": 0,
                    "steps": 20,
                    "cfg": 7,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1,
                    "model": ["4", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0]
                }
            },
            "4": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": "v1-5-pruned-emaonly.ckpt"}
            },
            "5": {
                "class_type": "EmptyLatentImage",
                "inputs": {"width": 1024, "height": 1024, "batch_size": 1}
            },
            "6": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": prompt, "clip": ["4", 1]}
            },
            "7": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": negative_prompt or "blurry, low quality",
                    "clip": ["4", 1]
                }
            }
        }

    def generate_video(self, **kwargs) -> Dict[str, Any]:
        """ComfyUI video generation using AnimateDiff"""
        return {
            "success": False,
            "error": "Video generation requires AnimateDiff nodes"
        }


def get_provider(
    provider_type: str,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    **kwargs
) -> AIProvider:
    """
    Factory function to get AI provider instance

    Args:
        provider_type: Type of provider (stable_diffusion, openai_dalle, etc.)
        api_key: API key for the provider
        base_url: Base URL for local providers
        **kwargs: Additional provider-specific arguments

    Returns:
        AIProvider instance

    Raises:
        ValueError: If provider type is not supported
    """
    provider_map = {
        "stable_diffusion": lambda: StableDiffusionProvider(api_key, base_url, kwargs.get("model")),
        "sd": lambda: StableDiffusionProvider(api_key, base_url, kwargs.get("model")),
        "openai_dalle": lambda: OpenAIDALLEProvider(api_key),
        "dalle": lambda: OpenAIDALLEProvider(api_key),
        "replicate": lambda: ReplicateProvider(api_key, kwargs.get("model")),
        "liblib": lambda: LibLibProvider(api_key, base_url),
        "comfyui": lambda: ComfyUIProvider(api_key, base_url),
    }

    provider_type = provider_type.lower().replace("-", "_")

    if provider_type not in provider_map:
        raise ValueError(
            f"Unsupported provider: {provider_type}. "
            f"Supported providers: {list(provider_map.keys())}"
        )

    return provider_map[provider_type]()


def load_provider_config(config_path: Optional[Path] = None) -> Dict[str, Dict]:
    """
    Load provider configurations from file

    Args:
        config_path: Path to config file (default: ~/.openfang/aigc_providers.json)

    Returns:
        Dictionary of provider configurations
    """
    if config_path is None:
        config_path = Path.home() / ".openfang" / "aigc_providers.json"

    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)

    # Default config
    return {
        "default_provider": "stable_diffusion",
        "providers": {
            "stable_diffusion": {
                "base_url": "http://127.0.0.1:7860",
                "enabled": True
            },
            "openai_dalle": {
                "enabled": False
            },
            "replicate": {
                "enabled": False
            }
        }
    }


if __name__ == "__main__":
    # Test provider instantiation
    print("Testing AI Providers...")

    # Test Stable Diffusion
    try:
        sd = get_provider("stable_diffusion", base_url="http://127.0.0.1:7860")
        print(f"✅ Stable Diffusion provider created: {sd.base_url}")
    except Exception as e:
        print(f"❌ Stable Diffusion provider failed: {e}")

    # Test OpenAI DALL-E
    try:
        dalle = get_provider("openai_dalle")
        print(f"✅ OpenAI DALL-E provider created")
    except Exception as e:
        print(f"❌ OpenAI DALL-E provider failed: {e}")

    # Load config
    config = load_provider_config()
    print(f"\n📋 Loaded provider config: {json.dumps(config, indent=2)}")
