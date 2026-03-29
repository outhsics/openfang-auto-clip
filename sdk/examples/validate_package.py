#!/usr/bin/env python3
"""
Package Validation Example

Demonstrates validating Level 2 packages.
"""

import sys
from pathlib import Path

# Add SDK to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from openfang_sdk import Client, ValidationError


def main():
    """Run validation example"""

    print("🔍 Package Validation Example")
    print("=" * 50)

    client = Client(base_url="http://localhost:8000")

    # Find a package to validate
    output_dir = Path.home() / ".openfang" / "output"
    packages = list(output_dir.glob("*.json"))

    if not packages:
        print(f"❌ No packages found in {output_dir}")
        print("   Please process a transcript first")
        return

    # Use the most recent package
    package_path = sorted(packages, key=lambda p: p.stat().st_mtime)[-1]

    print(f"\n📦 Validating: {package_path.name}")
    print(f"   Size: {package_path.stat().st_size} bytes")

    try:
        # Validate package
        result = client.validate_package(str(package_path))

        print("\n" + "=" * 50)
        print("📊 Validation Results")
        print("=" * 50)

        # Overall score
        print(f"\nOverall Score: {result['overall_score']}/10")
        print(f"Grade: {result['grade']}")

        # Production ready
        ready = "✅ Yes" if result['production_ready'] else "❌ No"
        print(f"Production Ready: {ready}")

        # Quality scores
        print("\n📈 Quality Scores:")
        for dimension, score in result['scores'].items():
            stars = "⭐" * int(score / 2)
            print(f"   {dimension.capitalize():20} {score:5.1f}/10  {stars}")

        # Copyright risk
        copyright = result['copyright_risk']
        print(f"\n🛡️  Copyright Risk:")
        print(f"   Risk Level: {copyright['risk_level']}")
        print(f"   Semantic Similarity: {copyright['semantic_similarity']*100:.1f}%")
        print(f"   Word Overlap: {copyright['word_overlap']*100:.1f}%")

        # Issues
        if result['issues']:
            print(f"\n⚠️  Issues ({len(result['issues'])}):")
            for issue in result['issues']:
                print(f"   • {issue}")

        # Recommendations
        if result['recommendations']:
            print(f"\n💡 Recommendations ({len(result['recommendations'])}):")
            for rec in result['recommendations']:
                print(f"   • {rec}")

        # Overall assessment
        print("\n" + "=" * 50)
        if result['production_ready']:
            print("✅ Package is production ready!")
        else:
            print("⚠️  Package needs improvement before production use")

    except ValidationError as e:
        print(f"\n❌ Validation failed: {e.message}")

    except Exception as e:
        print(f"\n❌ Error: {e}")

    client.close()

    print("\n✅ Validation complete!")


if __name__ == "__main__":
    main()
