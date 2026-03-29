# OpenFang Auto Clip - Examples Collection

**Version:** v0.3.0+
**Last Updated:** 2026-03-29

---

## 📚 Examples Overview

This directory contains practical examples for using OpenFang Auto Clip.

### Directory Structure

```
examples/
├── demo/                    # Demo transcript and output
├── level2_samples/          # Sample collection for testing
├── showcases/               # Showcase examples
├── tutorials/               # Tutorial scripts
└── examples.md              # This file
```

---

## 🚀 Quick Start Examples

### Example 1: First Time Setup

```bash
# Clone and install
git clone https://github.com/outhsics/openfang-auto-clip.git
cd openfang-auto-clip
pip install -e .

# Run environment check
python3 auto_clip.py --doctor

# Generate demo package
python3 auto_clip.py --demo-script-package
```

### Example 2: Level 2 with Custom Transcript

```bash
# Your transcript file
cat > my_video.srt << 'EOF'
1
00:00:00,000 --> 00:00:05,000
Welcome to this tutorial about Python programming.

2
00:00:05,000 --> 00:00:10,000
Today we'll learn about variables and data types.

3
00:00:10,000 --> 00:00:15,000
Let's start with a simple example.
EOF

# Generate Level 2 package
python3 auto_clip.py \
    --transform 2 \
    --transcript my_video.srt \
    "https://www.youtube.com/watch?v=demo"

# Review output
cat ~/.openfang/clips/script_packages/*/script_draft.md
```

### Example 3: Interactive Review

```bash
# Generate package first
python3 scripts/test_level2_complete.py --demo

# Review interactively
python3 scripts/interactive_review.py --latest

# In the interactive menu:
# - Choose 2 to review sections
# - Choose 4 to edit sections
# - Choose 5 to validate
# - Choose 6 to export
# - Choose 8 to save
```

---

## 📝 Content Type Examples

### Educational Content / 教育内容

**Transcript (`edu_science_quantum.srt`):**
```srt
1
00:00:00,000 --> 00:00:08,000
Quantum mechanics is the branch of physics that deals with the behavior of matter and light on the atomic and subatomic scale.

2
00:00:08,000 --> 00:00:16,000
It attempts to describe and account for the properties of molecules and atoms and their constituents—electrons, protons, neutrons, and other more esoteric particles such as quarks and gluons.

3
00:00:16,000 --> 00:00:24,000
Properties of matter and light on a scale that is typically smaller than a few nanometers require quantum mechanics for their description.
```

**Expected Output Type:** `EDUCATIONAL`

**Characteristics:**
- Clear explanations
- Technical concepts
- Structured information

### Tutorial Content / 教程内容

**Transcript (`tutorial_cake_baking.srt`):**
```srt
1
00:00:00,000 --> 00:00:05,000
Welcome to this cake baking tutorial for beginners.

2
00:00:05,000 --> 00:00:12,000
First, preheat your oven to 350 degrees Fahrenheit or 175 degrees Celsius.

3
00:00:12,000 --> 00:00:20,000
Next, mix the dry ingredients in one bowl and the wet ingredients in another bowl.
```

**Expected Output Type:** `TUTORIAL`

**Characteristics:**
- Step-by-step instructions
- Action-oriented
- Practical demonstrations

### Entertainment Content / 娱乐内容

**Transcript (`ent_comedy_standup.srt`):**
```srt
1
00:00:00,000 --> 00:00:06,000
So I was at the airport yesterday and something hilarious happened.

2
00:00:06,000 --> 00:00:14,000
The TSA agent asked me to take off my shoes, which I did, but then he also asked me to take off my socks!

3
00:00:14,000 --> 00:00:22,000
I said, buddy, if you wanted to see my feet that bad, you could have just bought me dinner first!
```

**Expected Output Type:** `ENTERTAINMENT`

**Characteristics:**
- Humorous tone
- Storytelling
- Engagement-focused

---

## 🔧 Advanced Examples

### Example 4: Custom Configuration

```python
import json
from pathlib import Path
from auto_clip import process_video

# Create custom config
config = {
    "default_duration": 90,  # Longer clips
    "min_duration": 45,
    "max_duration": 120,
    "target_platforms": ["youtube_shorts"],  # Just one platform
    "auto_caption": True,
    "whisper_model": "medium",  # Better quality
    "transform_level": 2
}

# Save config
config_path = Path.home() / ".openfang" / "auto_clip_config.json"
config_path.parent.mkdir(parents=True, exist_ok=True)
with open(config_path, "w") as f:
    json.dump(config, f, indent=2)

# Process with custom config
result = process_video(
    url="https://www.youtube.com/watch?v=VIDEO_ID",
    transform_level=2,
    transcript_path="transcript.srt"
)
```

### Example 5: Batch Processing

```python
from pathlib import Path
from scripts.level2_improved import build_improved_level2_package
from scripts.level2_validation import generate_validation_report
from auto_clip import build_transcript_payload

# Process multiple transcripts
transcripts_dir = Path("transcripts")
results = []

for transcript_file in transcripts_dir.glob("*.srt"):
    print(f"Processing {transcript_file.name}...")

    # Load transcript
    transcript = build_transcript_payload(transcript_file)

    # Generate package
    video_info = {
        "title": transcript_file.stem,
        "path": str(transcript_file)
    }

    package = build_improved_level2_package(
        video_info,
        transcript,
        transcript_file,
        {"default_duration": 60}
    )

    # Validate
    report = generate_validation_report(
        package,
        transcript["text"],
        transcript_file
    )

    # Store result
    results.append({
        "file": transcript_file.name,
        "status": report["overall_assessment"]["status"],
        "score": report["quality_scores"]["overall"],
        "grade": report["quality_scores"]["grade"]
    })

    # Print result
    emoji = "✅" if report["overall_assessment"]["status"] == "production_ready" else "⚠️"
    print(f"{emoji} {transcript_file.name}: {report['quality_scores']['overall']}/10 ({report['quality_scores']['grade']})")

# Summary
print(f"\nProcessed {len(results)} files")
production_ready = sum(1 for r in results if r["status"] == "production_ready")
print(f"Production ready: {production_ready}/{len(results)}")
```

### Example 6: Quality Comparison

```python
from scripts.compare_level2_improvements import run_comparison

# Compare original vs improved
result = run_comparison("transcript.srt")

# Access results
original_package = result["original"]
improved_package = result["improved"]
comparison_path = result["comparison"]

print(f"Comparison saved to: {comparison_path}")

# Check improvements
print("\nKey improvements:")
print("- Visual direction: Enhanced")
print("- Content adaptation: Added")
print("- Timing: Optimized")
```

### Example 7: Export Formats

```python
import json
from pathlib import Path

# Load package
package_path = Path("~/.openfang/clips/script_packages/TIMESTAMP/script_package.json")
package = json.load(package_path.expanduser())

# Export as Markdown
markdown_lines = [
    f"# {package['source']['title']}",
    "",
    "## Script Sections",
    ""
]

for section in package["script_sections"]:
    markdown_lines.extend([
        f"### {section['section']} ({section['duration']}s)",
        "",
        f"**Narration:** {section['narration']}",
        "",
        f"**On-Screen:** {section['on_screen_text']}",
        "",
        f"**Visual:** {section['visual_direction']}",
        "",
        "---",
        ""
    ])

# Save markdown
output_path = Path("export.md")
output_path.write_text("\n".join(markdown_lines))
print(f"Exported to: {output_path}")
```

---

## 🎯 Use Cases

### Use Case 1: Content Creator

**Scenario:** You have long-form videos and want to create shorts.

```bash
# Extract transcript (use your tool)
whisper video.mp4 --output_format srt > video.srt

# Generate Level 2 package
python3 auto_clip.py \
    --transform 2 \
    --transcript video.srt \
    "video.mp4"

# Review and edit
python3 scripts/interactive_review.py --latest

# Export for production
# Choose option 6, then 1 (Markdown)

# Use in video editor
# Import script_export.md and follow the visual direction
```

### Use Case 2: Educator

**Scenario:** Convert educational content into multiple short clips.

```python
# Script for processing educational content
from pathlib import Path
from scripts.level2_improved import build_improved_level2_package
from scripts.level2_validation import generate_validation_report

def process_educational_content(transcript_path: Path):
    """Process educational transcript with quality checks."""

    # Load and generate
    transcript = build_transcript_payload(transcript_path)

    package = build_improved_level2_package(
        {"title": transcript_path.stem, "path": str(transcript_path)},
        transcript,
        transcript_path,
        {"default_duration": 90}  # Longer for educational
    )

    # Validate
    report = generate_validation_report(
        package,
        transcript["text"],
        transcript_path
    )

    # Check educational quality
    if report["quality_scores"]["value_retention"] < 8.0:
        print("⚠️  Warning: Key educational points may be lost")
        print("   Please review the generated script")

    return package, report

# Use
package, report = process_educational_content(Path("lecture.srt"))
```

### Use Case 3: Agency Workflow

**Scenario:** Process multiple client videos efficiently.

```bash
#!/bin/bash
# agency_workflow.sh

# Configuration
TRANSCRIPT_DIR="transcripts/"
OUTPUT_DIR="output/"
CONFIG="agency_config.json"

# Process all transcripts
for transcript in $TRANSCRIPT_DIR/*.srt; do
    echo "Processing $transcript..."

    # Generate package
    python3 auto_clip.py \
        --transform 2 \
        --transcript "$transcript" \
        --config "$CONFIG" \
        "$transcript"

    # Validate
    python3 scripts/test_level2_complete.py \
        --transcript "$transcript"

    # Move to output
    LATEST=$(ls -td ~/.openfang/clips/script_packages_validated/*/ | head -1)
    cp -r "$LATEST" "$OUTPUT_DIR"

    echo "✅ Completed $transcript"
done

echo "All videos processed!"
```

---

## 📊 Performance Examples

### Benchmark: Processing Speed

```python
import time
from pathlib import Path
from scripts.level2_improved import build_improved_level2_package

# Benchmark processing time
transcripts = list(Path("transcripts/").glob("*.srt"))

for transcript_path in transcripts[:5]:  # Test 5 files
    start = time.time()

    # Process
    package = build_improved_level2_package(...)

    elapsed = time.time() - start

    print(f"{transcript_path.name}: {elapsed:.2f}s")

# Expected output:
# transcript1.srt: 2.34s
# transcript2.srt: 1.98s
# transcript3.srt: 2.67s
# transcript4.srt: 2.12s
# transcript5.srt: 2.45s
```

### Benchmark: Quality Scores

```python
from scripts.level2_validation import calculate_quality_scores

# Test quality on multiple samples
samples = [...]  # List of sample packages

for package, original in samples:
    scores = calculate_quality_scores(package, original)

    print(f"{package['source']['title']}: {scores['overall']}/10")

# Expected output:
# Educational Video: 9.2/10 (A)
# Tutorial Video: 8.8/10 (B+)
# Entertainment Video: 8.5/10 (B+)
```

---

## 🐛 Troubleshooting Examples

### Problem: Low Quality Scores

```python
# Diagnose and fix low quality scores
from scripts.level2_validation import calculate_quality_scores
from scripts.interactive_review import InteractiveReviewer

# Generate package
package = build_improved_level2_package(...)

# Check scores
scores = calculate_quality_scores(package, original_text)

# Identify low-scoring dimensions
low_scores = [
    dim for dim, score in scores["scores"].items()
    if score < 8.0
]

print(f"Low scores: {low_scores}")

# Fix interactively
reviewer = InteractiveReviewer(package_dir)
reviewer.review()  # Edit and improve

# Re-validate
new_scores = calculate_quality_scores(edited_package, original_text)
print(f"Improved: {new_scores['overall']}/10")
```

### Problem: High Copyright Risk

```python
from scripts.level2_validation import assess_copyright_risk

# Check copyright risk
risk = assess_copyright_risk(package, original_text)

if risk["risk_level"] in ["medium", "high"]:
    print("Copyright risk detected!")
    print(f"Risk factors: {len(risk['risk_factors'])}")

    # Review and edit
    for factor in risk["risk_factors"]:
        if factor["type"] == "direct_quotation":
            print("❌ Remove direct quotations")
        elif factor["type"] == "phrase_copying":
            print("❌ Rewrite copied phrases")
        elif factor["type"] == "high_similarity":
            print("❌ Make sections more different")

    # Use interactive review to fix
    reviewer = InteractiveReviewer(package_dir)
    reviewer.review()
```

---

## 🎓 Tutorial Scripts

### Tutorial 1: Your First Level 2 Package

```bash
#!/bin/bash
# tutorial_1_first_package.sh

echo "Welcome to OpenFang Auto Clip!"
echo "This tutorial will guide you through creating your first Level 2 package."
echo ""

# Step 1
echo "Step 1: Check environment"
python3 auto_clip.py --doctor
echo ""

# Step 2
echo "Step 2: Generate demo package"
python3 auto_clip.py --demo-script-package
echo ""

# Step 3
echo "Step 3: Review the output"
LATEST=$(ls -td ~/.openfang/clips/script_packages/*/ | head -1)
echo "Package location: $LATEST"
echo ""
cat "$LATEST/script_draft.md"
echo ""

# Step 4
echo "Step 4: Check quality"
cat "$LATEST/review_report.md"
echo ""

echo "✅ Tutorial complete! Your first Level 2 package is ready."
```

### Tutorial 2: Interactive Review

```bash
#!/bin/bash
# tutorial_2_interactive_review.sh

echo "Tutorial 2: Interactive Review"
echo "This tutorial teaches you how to review and edit packages."
echo ""

# Pre-requisite: Have a package ready
echo "Make sure you have generated a package first."
echo "Run: python3 auto_clip.py --demo-script-package"
echo ""

# Start interactive review
echo "Starting interactive review..."
python3 scripts/interactive_review.py --latest

echo ""
echo "✅ Tutorial complete! You now know how to review and edit packages."
```

### Tutorial 3: Quality Validation

```python
#!/usr/bin/env python3
# tutorial_3_quality_validation.py

"""
Tutorial 3: Quality Validation
This tutorial shows how to validate package quality.
"""

from pathlib import Path
from scripts.level2_validation import (
    calculate_quality_scores,
    assess_copyright_risk,
    generate_validation_report,
)
from scripts.level2_improved import build_improved_level2_package
from auto_clip import build_transcript_payload

print("Tutorial 3: Quality Validation")
print("=" * 70)

# Step 1: Load transcript
print("\nStep 1: Loading transcript...")
transcript_path = Path("tutorial_transcript.srt")
transcript = build_transcript_payload(transcript_path)
print(f"✅ Loaded {len(transcript['text'])} characters")

# Step 2: Generate package
print("\nStep 2: Generating package...")
package = build_improved_level2_package(
    {"title": "Tutorial", "path": str(transcript_path)},
    transcript,
    transcript_path,
    {"default_duration": 60}
)
print(f"✅ Generated {len(package['script_sections'])} sections")

# Step 3: Calculate quality scores
print("\nStep 3: Calculating quality scores...")
scores = calculate_quality_scores(package, transcript["text"])
print(f"✅ Overall: {scores['overall']}/10 ({scores['grade']})")

# Step 4: Assess copyright risk
print("\nStep 4: Assessing copyright risk...")
risk = assess_copyright_risk(package, transcript["text"])
print(f"✅ Risk Level: {risk['risk_level'].upper()}")

# Step 5: Generate full report
print("\nStep 5: Generating full validation report...")
report = generate_validation_report(
    package,
    transcript["text"],
    transcript_path
)
print(f"✅ Status: {report['overall_assessment']['status'].upper()}")

# Summary
print("\n" + "=" * 70)
print("Tutorial Complete!")
print(f"Quality Score: {scores['overall']}/10 ({scores['grade']})")
print(f"Copyright Risk: {risk['risk_level'].upper()}")
print(f"Status: {report['overall_assessment']['status'].upper()}")

if scores["overall"] >= 8.0 and risk["risk_level"] == "minimal":
    print("\n🎉 Excellent! Your package is production-ready.")
else:
    print("\n💡 Consider using interactive review to improve quality.")
```

---

## 📞 Need More Examples?

**Request Examples:**
- GitHub Issue: `example` label
- GitHub Discussion: `examples` category

**Contribute Examples:**
- Fork the repository
- Add your example to `examples/`
- Submit a pull request

---

**Last Updated:** 2026-03-29
**Version:** 1.0
**Status:** ✅ Ready to Use
