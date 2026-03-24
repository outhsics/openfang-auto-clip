#!/usr/bin/env python3
"""
Quick Start Guide for AIGC Integration

Simple examples to get started with AI image and video generation.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.aigc import generate_image, generate_video


def quick_image_example():
    """Generate your first AI image"""
    print("\n🎨 Generating your first AI image...\n")

    result = generate_image(
        prompt="A peaceful zen garden with cherry blossoms",
        provider="stable_diffusion",
        style="cinematic",
        width=1024,
        height=1024
    )

    if result.get("success"):
        print(f"✅ Success! Image saved to:")
        print(f"   {result.get('save_path')}")
        return True
    else:
        print(f"❌ Generation failed: {result.get('error')}")
        print("\n💡 Troubleshooting:")
        print("   1. Make sure Stable Diffusion WebUI is running")
        print("   2. Launch with: ./webui.sh --api")
        print("   3. Check it's accessible at http://127.0.0.1:7860")
        return False


def quick_video_example():
    """Generate your first AI video"""
    print("\n🎬 Generating your first AI video...\n")

    result = generate_video(
        prompt="Abstract gradient animation, smooth flowing colors",
        provider="stable_diffusion",
        duration=4.0,
        fps=30
    )

    if result.get("success"):
        print(f"✅ Success! Video saved to:")
        print(f"   {result.get('save_path')}")
        return True
    else:
        print(f"❌ Generation failed: {result.get('error')}")
        print("\n💡 Note: Video generation requires additional setup")
        print("   - Stable Diffusion Video extension")
        print("   - Or Deforum extension")
        return False


def quick_batch_example():
    """Generate multiple images at once"""
    print("\n📦 Generating multiple images...\n")

    from src.aigc import ImageGenerator, ImageStyle

    generator = ImageGenerator()

    prompts = [
        "Sunrise over mountains",
        "Ocean waves at sunset",
        "Forest path in autumn"
    ]

    print("Generating 3 images:")
    results = generator.generate_batch(
        prompts=prompts,
        style=ImageStyle.CINEMATIC,
        width=1024,
        height=1024,
        steps=15
    )

    for i, result in enumerate(results):
        if result.get("success"):
            print(f"  ✅ {i+1}. {result.get('save_path')}")

    return all(r.get("success") for r in results)


def quick_preset_example():
    """Generate using preset"""
    print("\n🎯 Generating YouTube thumbnail preset...\n")

    from src.aigc.image_generator import generate_preset

    result = generate_preset(
        "youtube_thumbnail",
        customizations={
            "prompt": "Epic gaming moment with dramatic lighting"
        }
    )

    if result.get("success"):
        print(f"✅ Thumbnail generated: {result.get('save_path')}")
        return True
    else:
        print(f"❌ Failed: {result.get('error')}")
        return False


def main():
    """Quick start menu"""
    print("=" * 60)
    print("OpenFang Auto Clip - AIGC Quick Start")
    print("=" * 60)

    print("\n📚 Prerequisites:")
    print("   1. Install Stable Diffusion WebUI")
    print("   2. Launch with: ./webui.sh --api")
    print("   3. Verify it's running at http://127.0.0.1:7860")

    print("\n🚀 Quick Start Options:")
    print("   1 - Generate your first image")
    print("   2 - Generate your first video")
    print("   3 - Generate multiple images (batch)")
    print("   4 - Generate using preset")
    print("   all - Run all examples")
    print("   q - Quit")

    choice = input("\nSelect option: ").strip().lower()

    if choice == "q":
        return

    success_count = 0
    total_count = 0

    if choice == "1" or choice == "all":
        total_count += 1
        if quick_image_example():
            success_count += 1

    if choice == "2" or choice == "all":
        total_count += 1
        if quick_video_example():
            success_count += 1

    if choice == "3" or choice == "all":
        total_count += 1
        if quick_batch_example():
            success_count += 1

    if choice == "4" or choice == "all":
        total_count += 1
        if quick_preset_example():
            success_count += 1

    if choice not in ["1", "2", "3", "4", "all"]:
        print("❌ Invalid choice!")
        return

    print("\n" + "=" * 60)
    print(f"Results: {success_count}/{total_count} successful")

    if success_count == total_count:
        print("🎉 All examples completed successfully!")
        print("\n📖 Next steps:")
        print("   - Try different prompts and styles")
        print("   - Check docs/AIGC_INTEGRATION.md for more details")
        print("   - Run examples/aigc_example.py for advanced examples")
    else:
        print("⚠️  Some examples failed. Check the error messages above.")

    print("=" * 60)


if __name__ == "__main__":
    main()
