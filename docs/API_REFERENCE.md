# OpenFang Auto Clip - API Documentation

**Version:** v0.3.0+
**Last Updated:** 2026-03-29

---

## 📖 Table of Contents

1. [Quick Start](#quick-start)
2. [CLI API](#cli-api)
3. [Python API](#python-api)
4. [Level 2 API](#level-2-api)
5. [Validation API](#validation-api)
6. [Examples](#examples)

---

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/outhsics/openfang-auto-clip.git
cd openfang-auto-clip
pip install -e .
```

### Basic Usage

```python
from auto_clip import process_video

# Process a video
result = process_video(
    url="https://www.youtube.com/watch?v=VIDEO_ID",
    transform_level=2,
    transcript_path="transcript.srt"
)
```

---

## 🔧 CLI API

### Main Command

```bash
python3 auto_clip.py [OPTIONS] URL
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--transform` | int | `1` | Transformation level (0-3) |
| `--transcript` | str | `None` | Path to transcript file |
| `--output-dir` | str | `~/.openfang/clips/` | Output directory |
| `--config` | str | `~/.openfang/auto_clip_config.json` | Config file path |
| `--doctor` | flag | `False` | Check environment |
| `--dry-run` | flag | `False` | Show plan without executing |
| `--demo-script-package` | flag | `False` | Generate demo package |
| `--review-package` | str | `None` | Review existing package |

### Examples

```bash
# Level 2 transformation with transcript
python3 auto_clip.py \
    --transform 2 \
    --transcript video.srt \
    "https://www.youtube.com/watch?v=VIDEO_ID"

# Generate demo package
python3 auto_clip.py --demo-script-package

# Review existing package
python3 auto_clip.py --review-package ~/.openfang/clips/script_packages/TIMESTAMP

# Environment check
python3 auto_clip.py --doctor
```

---

## 🐍 Python API

### Main Functions

#### `process_video()`

Process a video through the Level 2 pipeline.

```python
def process_video(
    url: str,
    transform_level: int = 1,
    transcript_path: Optional[str] = None,
    config: Optional[dict] = None
) -> dict
```

**Parameters:**
- `url` (str): Video URL or file path
- `transform_level` (int): 0=None, 1=Visual, 2=Script, 3=Complete
- `transcript_path` (str, optional): Path to transcript file
- `config` (dict, optional): Configuration overrides

**Returns:**
```python
{
    "status": "success",
    "level": 2,
    "package_dir": "/path/to/package",
    "transcript_path": "/path/to/transcript",
    "message": "Package generated successfully"
}
```

**Example:**
```python
from auto_clip import process_video

result = process_video(
    url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    transform_level=2,
    transcript_path="transcript.srt"
)

print(result["package_dir"])
```

#### `load_config()`

Load configuration from file.

```python
def load_config() -> dict
```

**Returns:**
```python
{
    "default_duration": 60,
    "min_duration": 30,
    "max_duration": 90,
    "target_platforms": ["tiktok", "shorts", "reels"],
    "auto_caption": True,
    "whisper_model": "base",
    "transform_level": 1
}
```

#### `build_doctor_report()`

Generate environment health report.

```python
def build_doctor_report() -> dict
```

**Returns:**
```python
{
    "checks": [
        {
            "name": "python",
            "status": "ok",
            "detail": "3.9.0",
            "required": True
        },
        # ... more checks
    ]
}
```

---

## 🎯 Level 2 API

### Generation Functions

#### `build_level2_script_package()`

Build a Level 2 script package (original implementation).

```python
def build_level2_script_package(
    video_info: dict,
    transcript_payload: dict,
    transcript_path: Path,
    config: dict
) -> dict
```

**Parameters:**
- `video_info` (dict): Video metadata
- `transcript_payload` (dict): Parsed transcript with text and segments
- `transcript_path` (Path): Path to transcript file
- `config` (dict): Configuration dictionary

**Returns:**
```python
{
    "milestone": "level2_transcript_to_script_package",
    "source": {
        "title": "Video Title",
        "path": "/path/to/transcript",
        "language": "en",
        "segment_count": 10
    },
    "script_sections": [...],
    "shot_plan": [...],
    "review_rubric": [...],
    "voiceover_notes": [...],
    "asset_requests": [...]
}
```

#### `build_improved_level2_package()`

Build an improved Level 2 package with content-aware generation.

```python
from scripts.level2_improved import build_improved_level2_package

def build_improved_level2_package(
    video_info: dict,
    transcript_payload: dict,
    transcript_path: Path,
    config: dict
) -> dict
```

**Enhanced Features:**
- Content type detection
- Content-aware narration
- Detailed visual direction
- Adaptive timing

**Example:**
```python
from scripts.level2_improved import build_improved_level2_package
from auto_clip import build_transcript_payload

# Load transcript
transcript = build_transcript_payload(Path("video.srt"))

# Generate package
package = build_improved_level2_package(
    video_info={"title": "My Video", "path": "video.srt"},
    transcript_payload=transcript,
    transcript_path=Path("video.srt"),
    config={"default_duration": 60}
)

print(f"Content Type: {package['source']['content_type']}")
print(f"Sections: {len(package['script_sections'])}")
```

### Transcript Processing

#### `build_transcript_payload()`

Parse and normalize transcript file.

```python
def build_transcript_payload(transcript_path: Path) -> dict
```

**Returns:**
```python
{
    "text": "Full transcript text...",
    "segments": [
        {
            "start": 0.0,
            "end": 4.5,
            "text": "First segment text"
        },
        # ... more segments
    ]
}
```

#### `detect_transcript_language()`

Detect transcript language (English or Chinese).

```python
def detect_transcript_language(text: str) -> str
```

**Returns:** `"en"` or `"zh"`

#### `detect_content_type()`

Detect content type from transcript.

```python
from scripts.level2_improved import detect_content_type, ContentType

def detect_content_type(
    transcript: dict,
    metadata: dict
) -> ContentType
```

**Returns:** `ContentType.EDUCATIONAL`, `ENTERTAINMENT`, `TUTORIAL`, or `GENERAL`

---

## ✅ Validation API

### Quality Scoring

#### `calculate_quality_scores()`

Calculate comprehensive quality scores.

```python
from scripts.level2_validation import calculate_quality_scores

def calculate_quality_scores(
    package: dict,
    original_transcript: str
) -> dict
```

**Returns:**
```python
{
    "scores": {
        "coherence": 8.5,
        "actionability": 9.0,
        "originality": 8.0,
        "value_retention": 8.5
    },
    "overall": 8.5,
    "is_production_ready": True,
    "is_acceptable": True,
    "grade": "B+"
}
```

**Example:**
```python
from scripts.level2_validation import calculate_quality_scores

scores = calculate_quality_scores(package, original_text)

if scores["is_production_ready"]:
    print("Ready for production!")
else:
    print(f"Score: {scores['overall']}/10")
    print("Needs improvement")
```

### Copyright Assessment

#### `assess_copyright_risk()`

Assess copyright risk of generated script.

```python
from scripts.level2_validation import assess_copyright_risk

def assess_copyright_risk(
    package: dict,
    original_transcript: str
) -> dict
```

**Returns:**
```python
{
    "risk_level": "low",  # minimal, low, medium, high
    "total_risk_score": 0.3,
    "recommendation": "approve",
    "risk_factors": [...],
    "safe_for_commercial_use": True
}
```

### Similarity Checking

#### `check_semantic_similarity()`

Check semantic similarity between texts.

```python
from scripts.level2_validation import check_semantic_similarity

def check_semantic_similarity(
    original_text: str,
    new_text: str,
    threshold: float = 0.75
) -> dict
```

**Returns:**
```python
{
    "similarity_score": 0.65,
    "is_too_similar": False,
    "recommendation": "approve",
    "threshold": 0.75,
    "method": "word_overlap_jaccard",
    "details": {...}
}
```

### Comprehensive Validation

#### `generate_validation_report()`

Generate complete validation report.

```python
from scripts.level2_validation import generate_validation_report

def generate_validation_report(
    package: dict,
    original_transcript: str,
    transcript_path: Path
) -> dict
```

**Returns:**
```python
{
    "timestamp": "2026-03-29T...",
    "quality_scores": {...},
    "copyright_assessment": {...},
    "key_point_retention": {...},
    "section_similarities": [...],
    "overall_assessment": {
        "status": "production_ready",
        "recommendation": "...",
        "confidence": "high"
    }
}
```

---

## 📚 Examples

### Example 1: Basic Level 2 Generation

```python
from auto_clip import process_video

# Generate Level 2 package
result = process_video(
    url="https://www.youtube.com/watch?v=VIDEO_ID",
    transform_level=2,
    transcript_path="transcript.srt"
)

# Check result
if result["status"] == "success":
    print(f"Package: {result['package_dir']}")
else:
    print(f"Error: {result['message']}")
```

### Example 2: Improved Generation with Validation

```python
from scripts.level2_improved import build_improved_level2_package
from scripts.level2_validation import generate_validation_report, save_validation_report
from auto_clip import build_transcript_payload
from pathlib import Path

# Setup
transcript_path = Path("video.srt")
video_info = {"title": "My Video", "path": str(transcript_path)}

# Load transcript
transcript = build_transcript_payload(transcript_path)

# Generate improved package
package = build_improved_level2_package(
    video_info,
    transcript,
    transcript_path,
    {"default_duration": 60}
)

# Validate
original_text = transcript["text"]
report = generate_validation_report(package, original_text, transcript_path)

# Save validation
save_validation_report(Path(package_dir), report)

# Check results
if report["overall_assessment"]["status"] == "production_ready":
    print("✅ Ready for production!")
else:
    print("⚠️  Needs revision")
```

### Example 3: Interactive Review

```python
from scripts.interactive_review import InteractiveReviewer
from pathlib import Path

# Load package
reviewer = InteractiveReviewer(Path("path/to/package"))

# Start interactive session
reviewer.review()
```

### Example 4: Custom Content Type

```python
from scripts.level2_improved import detect_content_type, ContentType

# Detect content type
content_type = detect_content_type(transcript, metadata)

# Generate type-specific script
if content_type == ContentType.EDUCATIONAL:
    print("Generating educational script...")
elif content_type == ContentType.TUTORIAL:
    print("Generating tutorial script...")
```

### Example 5: Batch Processing

```python
from pathlib import Path
from scripts.level2_improved import build_improved_level2_package
from scripts.level2_validation import generate_validation_report

# Process multiple transcripts
transcripts = Path("transcripts/").glob("*.srt")

for transcript_path in transcripts:
    # Generate package
    package = build_improved_level2_package(...)

    # Validate
    report = generate_validation_report(...)

    # Save if good
    if report["overall_assessment"]["status"] == "production_ready":
        print(f"✅ {transcript_path.name} - Ready")
    else:
        print(f"⚠️  {transcript_path.name} - Needs revision")
```

---

## 🔧 Configuration

### Config File Structure

```json
{
  "default_duration": 60,
  "min_duration": 30,
  "max_duration": 90,
  "target_platforms": ["tiktok", "shorts", "reels"],
  "auto_caption": true,
  "whisper_model": "base",
  "transform_level": 1,
  "openfang_api": "http://127.0.0.1:4200"
}
```

### Environment Variables

```bash
# Optional: Set API keys
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-..."

# Optional: Set paths
export OPENFANG_OUTPUT_DIR="/custom/output/path"
export OPENFANG_CONFIG_FILE="/custom/config.json"
```

---

## 🐛 Error Handling

### Common Exceptions

#### `ValueError`

Raised when:
- Transcript is too short
- Invalid transform level
- Missing required parameters

**Example:**
```python
try:
    result = process_video(url, transform_level=2)
except ValueError as e:
    print(f"Invalid input: {e}")
```

#### `FileNotFoundError`

Raised when:
- Transcript file not found
- Video file not accessible

**Example:**
```python
try:
    result = process_video(url, transcript_path="missing.srt")
except FileNotFoundError as e:
    print(f"File not found: {e}")
```

---

## 📞 Support

- **Documentation:** See `docs/` directory
- **Issues:** GitHub Issues
- **Discussions:** GitHub Discussions

---

**Last Updated:** 2026-03-29
**Version:** 1.0
**Status:** ✅ Production Ready
