#!/usr/bin/env python3
"""
AIGC Example Scripts for OpenFang Auto Clip

Demonstrates various AI image and video generation capabilities.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.aigc import (
    ImageGenerator,
    VideoGenerator,
    generate_image,
    generate_video,
    ImageStyle,
    VideoStyle
)


def example_1_basic_image_generation():
    """Example 1: Basic image generation"""
    print("\n=== Example 1: Basic Image Generation ===\n")

    result = generate_image(
        prompt="A serene mountain landscape at sunset",
        provider="stable_diffusion",
        width=1024,
        height=1024,
        steps=20
    )

    if result.get("success"):
        print(f"✅ Image generated: {result.get('save_path')}")
    else:
        print(f"❌ Generation failed: {result.get('error')}")


def example_2_styled_images():
    """Example 2: Generate images with different styles"""
    print("\n=== Example 2: Styled Images ===\n")

    styles = [
        ImageStyle.CINEMATIC,
        ImageStyle.ANIME,
        ImageStyle.CYBERPUNK,
        ImageStyle.WATERCOLOR
    ]

    generator = ImageGenerator()

    for style in styles:
        print(f"Generating {style.value} style...")
        result = generator.generate(
            prompt="A beautiful portrait of a young woman",
            style=style,
            width=768,
            height=1024,
            steps=15
        )

        if result.get("success"):
            print(f"  ✅ Saved to: {result.get('save_path')}")


def example_3_image_variations():
    """Example 3: Generate variations of a prompt"""
    print("\n=== Example 3: Image Variations ===\n")

    generator = ImageGenerator()

    variations = generator.generate_variations(
        base_prompt="A futuristic city skyline at night",
        num_variations=4,
        width=1024,
        height=768,
        steps=20
    )

    print(f"Generated {len(variations)} variations:")
    for i, result in enumerate(variations):
        if result.get("success"):
            print(f"  {i+1}. {result.get('save_path')}")


def example_4_batch_generation():
    """Example 4: Batch generate multiple images"""
    print("\n=== Example 4: Batch Generation ===\n")

    prompts = [
        "A peaceful zen garden",
        "A bustling coffee shop",
        "A library with ancient books",
        "A rooftop city view",
        "A cozy cabin in the woods"
    ]

    generator = ImageGenerator()

    results = generator.generate_batch(
        prompts=prompts,
        style=ImageStyle.REALISTIC,
        width=1024,
        height=1024,
        steps=15
    )

    print(f"Generated {len(results)} images:")
    for i, result in enumerate(results):
        if result.get("success"):
            print(f"  {i+1}. {prompts[i][:30]}... → {result.get('save_path')}")


def example_5_basic_video_generation():
    """Example 5: Basic video generation"""
    print("\n=== Example 5: Basic Video Generation ===\n")

    result = generate_video(
        prompt="Clouds moving slowly over a mountain range",
        provider="stable_diffusion",
        duration=4.0,
        fps=30
    )

    if result.get("success"):
        print(f"✅ Video generated: {result.get('save_path')}")
    else:
        print(f"❌ Generation failed: {result.get('error')}")


def example_6_looping_video():
    """Example 6: Generate looping background video"""
    print("\n=== Example 6: Looping Video ===\n")

    generator = VideoGenerator()

    result = generator.generate_loop(
        prompt="Abstract geometric shapes floating and rotating",
        duration=10.0,
        width=1920,
        height=1080
    )

    if result.get("success"):
        print(f"✅ Looping video: {result.get('save_path')}")
    else:
        print(f"❌ Failed: {result.get('error')}")


def example_7_social_media_video():
    """Example 7: Generate vertical video for social media"""
    print("\n=== Example 7: Social Media Video ===\n")

    from src.aigc.video_generator import generate_preset_video

    result = generate_preset_video(
        preset_name="social_short",
        prompt="Fashion model posing with dynamic lighting",
        duration=15.0
    )

    if result.get("success"):
        print(f"✅ Social media video: {result.get('save_path')}")
    else:
        print(f"❌ Failed: {result.get('error')}")


def example_8_multi_scene_video():
    """Example 8: Generate multi-scene video"""
    print("\n=== Example 8: Multi-Scene Video ===\n")

    generator = VideoGenerator()

    script = "A journey through different landscapes"
    scenes = [
        "Sunrise over mountains with golden light",
        "Waterfall cascading into a clear pool",
        "Sunset over a calm lake",
        "Stars appearing in the night sky"
    ]

    result = generator.text_to_video(
        script=script,
        scene_descriptions=scenes,
        duration=3.0,
        fps=30,
        transition="fade"
    )

    if result.get("success"):
        print(f"✅ Combined video: {result.get('save_path')}")
        print(f"   Scenes: {len(result.get('scenes', []))}")
    else:
        print(f"❌ Failed: {result.get('error')}")


def example_9_image_to_video():
    """Example 9: Animate static image"""
    print("\n=== Example 9: Image to Video ===\n")

    generator = VideoGenerator()

    # Note: Requires an existing image file
    image_path = Path("input_image.jpg")

    if not image_path.exists():
        print(f"⚠️  Please provide an image at {image_path}")
        print("   This example demonstrates the API for image-to-video generation")
        return

    result = generator.image_to_video(
        image_path=image_path,
        motion_prompt="Slow zoom in with subtle rotation",
        duration=5.0,
        motion_strength=0.5
    )

    if result.get("success"):
        print(f"✅ Animated video: {result.get('save_path')}")
    else:
        print(f"❌ Failed: {result.get('error')}")


def example_10_custom_provider():
    """Example 10: Use custom AI provider"""
    print("\n=== Example 10: Custom Provider ===\n")

    from src.aigc import get_provider

    # Try to connect to ComfyUI
    try:
        provider = get_provider(
            "comfyui",
            base_url="http://127.0.0.1:8188"
        )

        generator = ImageGenerator(provider=provider)

        result = generator.generate(
            prompt="A steampunk airship in the clouds",
            width=1024,
            height=1024
        )

        if result.get("success"):
            print(f"✅ Generated with ComfyUI: {result.get('save_path')}")
        else:
            print(f"⚠️  ComfyUI returned: {result.get('error')}")

    except Exception as e:
        print(f"⚠️  Could not connect to ComfyUI: {e}")
        print("   Make sure ComfyUI is running at http://127.0.0.1:8188")


def example_11_generation_history():
    """Example 11: View generation history"""
    print("\n=== Example 11: Generation History ===\n")

    generator = ImageGenerator()

    # Generate some images
    for i in range(3):
        generator.generate(
            prompt=f"Test image {i+1}",
            width=512,
            height=512,
            steps=10
        )

    # View history
    history = generator.get_history(limit=10)

    print(f"Recent generations ({len(history)}):")
    for item in history:
        print(f"  - {item['timestamp']}: {item['prompt']}")


def example_12_preset_images():
    """Example 12: Generate preset images"""
    print("\n=== Example 12: Preset Images ===\n")

    from src.aigc.image_generator import generate_preset

    presets = [
        "youtube_thumbnail",
        "video_background",
        "social_media_post"
    ]

    for preset in presets:
        print(f"Generating {preset}...")
        result = generate_preset(preset)

        if result.get("success"):
            print(f"  ✅ {result.get('save_path')}")
        else:
            print(f"  ⚠️  {result.get('error')}")


def main():
    """Run all examples"""
    print("=" * 60)
    print("OpenFang Auto Clip - AIGC Examples")
    print("=" * 60)

    examples = [
        ("Basic Image Generation", example_1_basic_image_generation),
        ("Styled Images", example_2_styled_images),
        ("Image Variations", example_3_image_variations),
        ("Batch Generation", example_4_batch_generation),
        ("Basic Video Generation", example_5_basic_video_generation),
        ("Looping Video", example_6_looping_video),
        ("Social Media Video", example_7_social_media_video),
        ("Multi-Scene Video", example_8_multi_scene_video),
        ("Image to Video", example_9_image_to_video),
        ("Custom Provider", example_10_custom_provider),
        ("Generation History", example_11_generation_history),
        ("Preset Images", example_12_preset_images),
    ]

    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")

    print("\nOptions:")
    print("  all   - Run all examples")
    print("  1-12  - Run specific example")
    print("  q     - Quit")

    choice = input("\nSelect example to run: ").strip().lower()

    if choice == "q":
        print("Goodbye!")
        return

    if choice == "all":
        for name, func in examples:
            try:
                func()
            except Exception as e:
                print(f"\n❌ Error in {name}: {e}")
    elif choice.isdigit() and 1 <= int(choice) <= len(examples):
        idx = int(choice) - 1
        name, func = examples[idx]
        try:
            func()
        except Exception as e:
            print(f"\n❌ Error: {e}")
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    main()
