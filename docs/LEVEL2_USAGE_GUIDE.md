# Level 2 Usage Guide / Level 2 使用指南

**Version:** v0.3.0+
**Last Updated:** 2026-03-29
**Status:** ✅ Production Ready

---

## 📖 What is Level 2? / Level 2 是什么？

Level 2 is the **Script Regeneration** transformation level that converts original video transcripts into fresh, copyright-safe script packages.

Level 2 是**脚本重新生成**转换级别，将原始视频转录转换为全新的、版权安全的脚本包。

### Key Features / 主要功能

- ✅ **Content-Aware Generation** - Adapts to educational, entertainment, tutorial content
- ✅ **Detailed Visual Direction** - Production-ready shot specifications
- ✅ **Quality Validation** - Multi-dimensional scoring and feedback
- ✅ **Copyright Safety** - Risk assessment and similarity checking
- ✅ **Interactive Review** - Edit and refine generated scripts

---

## 🚀 Quick Start / 快速开始

### Prerequisites / 前置要求

```bash
# Install dependencies
pip install -e .

# Verify installation
python3 auto_clip.py --doctor
```

### Basic Usage / 基本用法

```bash
# Method 1: Generate from transcript file
python3 auto_clip.py --transform 2 \
    --transcript path/to/transcript.srt \
    "https://www.youtube.com/watch?v=VIDEO_ID"

# Method 2: Generate demo package
python3 auto_clip.py --demo-script-package

# Method 3: Use improved generation
python3 scripts/test_level2_complete.py --demo
```

---

## 📋 Input Requirements / 输入要求

### Transcript Formats / 支持的转录格式

Level 2 accepts multiple transcript formats:

| Format | Extension | Example |
|--------|-----------|---------|
| SubRip | `.srt` | `transcript.srt` |
| WebVTT | `.vtt` | `captions.vtt` |
| Plain Text | `.txt` | `transcript.txt` |
| JSON | `.json` | `transcript.json` |
| Markdown | `.md` | `script.md` |

### Transcript Quality / 转录质量要求

**Minimum Requirements:**
- At least 3 sentences
- 50+ words recommended
- Clear, readable text
- No excessive noise

**Best Results:**
- Well-formatted subtitles
- Speaker identification
- Time stamps (for anchoring)
- Clean punctuation

---

## 🎯 Content Types / 内容类型

Level 2 automatically detects and adapts to different content types:

### 1. Educational / 教育类

**Characteristics:**
- Explains concepts
- Teaches skills
- Provides information

**Output Style:**
- Clear explanations
- Logical structure
- Professional tone
- Diagram suggestions

### 2. Entertainment / 娱乐类

**Characteristics:**
- Comedy, humor
- Storytelling
- Engagement-focused

**Output Style:**
- Energetic tone
- Dynamic pacing
- Humorous elements
- Entertainment value

### 3. Tutorial / 教程类

**Characteristics:**
- Step-by-step instructions
- How-to guides
- Demonstrations

**Output Style:**
- Clear steps
- Practical focus
- Action-oriented
- Visual demonstrations

### 4. General / 通用类

**Characteristics:**
- Mixed content
- No clear category
- Default fallback

**Output Style:**
- Balanced approach
- Professional tone
- Clear structure
- Wide applicability

---

## 📦 Output Structure / 输出结构

### Generated Files / 生成的文件

Level 2 generates a complete script package directory:

```
~/.openfang/clips/script_packages/TIMESTAMP_Title/
├── script_package.json           # Machine-readable package
├── script_draft.md               # Human-readable script
├── production_blueprint.json     # Production specifications
├── operator_handoff.json         # Handoff documentation
├── review_report.json            # Quality assessment
├── review_report.md              # Review summary
└── validation_report.md          # Validation results (if validated)
```

### Script Sections / 脚本结构

Each package contains 4-6 sections:

1. **Hook / 开场** (10-15s)
   - Grab attention
   - State core idea
   - Set expectations

2. **Beat 1-N / 重点** (6-12s each)
   - Main content points
   - Supporting details
   - Examples and illustrations

3. **Close / 收尾** (8-12s)
   - Summarize key points
   - Call to action
   - Final takeaway

---

## 🔧 Advanced Usage / 高级用法

### 1. Improved Generation / 改进生成

Use the enhanced Level 2 implementation:

```bash
python3 scripts/test_level2_complete.py \
    --transcript path/to/transcript.srt
```

**Benefits:**
- Content-aware generation
- Better visual direction
- Adaptive timing
- Quality validation

### 2. Interactive Review / 交互式审查

Review and edit generated packages:

```bash
# Review latest package
python3 scripts/interactive_review.py --latest

# Review specific package
python3 scripts/interactive_review.py \
    --package ~/.openfang/clips/script_packages/TIMESTAMP_Title
```

**Features:**
- Section-by-section review
- Edit narration and visuals
- Real-time quality feedback
- Multi-format export

### 3. Quality Validation / 质量验证

Generate comprehensive validation reports:

```python
from scripts.level2_validation import (
    generate_validation_report,
    save_validation_report,
)

# Load package
with open("script_package.json") as f:
    package = json.load(f)

# Generate report
report = generate_validation_report(
    package,
    original_transcript,
    transcript_path
)

# Save report
save_validation_report(package_dir, report)
```

**Includes:**
- Quality scores (0-10)
- Copyright risk assessment
- Key point retention
- Actionable recommendations

### 4. Comparison Tools / 对比工具

Compare original vs improved:

```bash
python3 scripts/compare_level2_improvements.py --demo
```

**Output:**
- Side-by-side comparison
- Before/after metrics
- Improvement analysis

---

## 📊 Quality Scoring / 质量评分

### Score Dimensions / 评分维度

#### 1. Coherence / 连贯性 (0-10)

**Measures:**
- Logical flow
- Clear structure
- Smooth transitions
- Complete sections

**Target:** 8.0+/10 for production

#### 2. Actionability / 可操作性 (0-10)

**Measures:**
- Visual direction specificity
- Shot plan details
- Production feasibility
- Asset requirements

**Target:** 8.0+/10 for production

#### 3. Originality / 原创性 (0-10)

**Measures:**
- Difference from source
- Fresh expression
- Creative angle
- Copyright safety

**Target:** 9.0+/10 for production

#### 4. Value Retention / 价值保留 (0-10)

**Measures:**
- Key points preserved
- Core message maintained
- Educational value kept
- No information loss

**Target:** 8.0+/10 for production

### Overall Score / 总体评分

```
Overall = (Coherence + Actionability + Originality + Value Retention) / 4
```

**Grades:**
- **A** (9.0-10.0): Production ready
- **B+** (8.0-8.9): Excellent
- **B** (7.0-7.9): Good
- **C** (6.0-6.9): Acceptable
- **F** (0-5.9): Needs revision

---

## ⚖️ Copyright Safety / 版权安全

### Risk Assessment / 风险评估

Level 2 includes automatic copyright risk checking:

**Risk Levels:**
- **Minimal** (< 0.2): Safe for commercial use
- **Low** (0.2-0.5): Review recommended
- **Medium** (0.5-1.0): Revision required
- **High** (> 1.0): Major revision needed

### Risk Factors / 风险因素

1. **Direct Quotation** - Verbatim copying
2. **Phrase Copying** - Similar expressions
3. **High Similarity** - Close paraphrasing

### Best Practices / 最佳实践

**To Ensure Copyright Safety:**
- ✅ Use original language and expression
- ✅ Add own examples and illustrations
- ✅ Change structure and organization
- ✅ Verify with validation tools
- ❌ Avoid direct quotation
- ❌ Don't copy sentence structure
- ❌ Minimize phrase overlap

---

## 🎨 Customization / 自定义

### Configuration Options / 配置选项

Edit `~/.openfang/auto_clip_config.json`:

```json
{
  "default_duration": 60,
  "min_duration": 30,
  "max_duration": 90,
  "target_platforms": ["tiktok", "shorts", "reels"],
  "auto_caption": true,
  "whisper_model": "base",
  "transform_level": 2
}
```

### Platform Targets / 目标平台

Supported platforms:
- **TikTok** - 9:16, 15-60s
- **YouTube Shorts** - 9:16, 30-60s
- **Instagram Reels** - 9:16, 15-90s
- **Douyin** - 抖音, 9:16, 15-60s

---

## 🐛 Troubleshooting / 故障排除

### Common Issues / 常见问题

#### 1. "Transcript not found"

**Cause:** Transcript file missing or wrong path

**Solution:**
```bash
# Check file exists
ls -la path/to/transcript.srt

# Use absolute path
python3 auto_clip.py --transform 2 \
    --transcript /full/path/to/transcript.srt \
    "VIDEO_URL"
```

#### 2. "Low quality scores"

**Cause:** Various factors (see quality report)

**Solutions:**
- Review quality report for specific issues
- Use interactive review to edit sections
- Improve transcript quality
- Try different content type

#### 3. "High copyright risk"

**Cause:** Too similar to original

**Solutions:**
- Edit narration to be more different
- Change examples and illustrations
- Modify structure and organization
- Re-validate after changes

#### 4. "Visual direction too vague"

**Cause:** Generic templates used

**Solutions:**
- Use improved generation (`test_level2_complete.py`)
- Edit visual direction interactively
- Add specific shot details
- Include camera movements

---

## 📚 Further Reading / 延伸阅读

### Documentation / 文档

- `ROADMAP_v0.4.0.md` - Development roadmap
- `docs/LEVEL2_IMPROVEMENT_ANALYSIS.md` - Technical details
- `docs/INTERACTIVE_REVIEW_GUIDE.md` - Review tool guide
- `docs/PROGRESS_SUMMARY.md` - Project progress

### Code / 代码

- `auto_clip.py` - Main implementation
- `scripts/level2_improved.py` - Enhanced generation
- `scripts/level2_validation.py` - Validation system
- `scripts/interactive_review.py` - Review tool

### Examples / 示例

- `examples/demo/` - Demo transcript and output
- `examples/level2_samples/` - Sample collection
- `examples/showcases/` - Showcase examples

---

## 💡 Tips & Best Practices / 最佳实践

### For Best Results / 获得最佳结果

1. **Start with Quality Transcripts**
   - Use accurate, well-formatted transcripts
   - Include time stamps when possible
   - Clean up noise and errors

2. **Review Generated Output**
   - Always review quality scores
   - Check copyright risk assessment
   - Verify key point retention

3. **Edit and Refine**
   - Use interactive review tool
   - Improve low-scoring sections
   - Add specific visual direction

4. **Validate Before Production**
   - Run comprehensive validation
   - Check all risk factors
   - Ensure production readiness

5. **Export and Use**
   - Export to preferred format
   - Use in video production
   - Collect feedback for improvement

### Workflow / 工作流程

```
1. Prepare transcript
   ↓
2. Generate Level 2 package
   ↓
3. Review quality scores
   ↓
4. Edit sections interactively
   ↓
5. Validate changes
   ↓
6. Export for production
   ↓
7. Use in video creation
```

---

## 🎓 Tutorial / 教程

### Complete Workflow Example / 完整工作流程示例

```bash
# Step 1: Get transcript
# (Use your preferred method: Whisper, manual, etc.)

# Step 2: Generate Level 2 package
python3 auto_clip.py --transform 2 \
    --transcript my_video.srt \
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Step 3: Review the package
cd ~/.openfang/clips/script_packages/TIMESTAMP_My_Video/
cat script_draft.md

# Step 4: Check quality
cat review_report.md

# Step 5: Edit interactively
python3 scripts/interactive_review.py \
    --package ~/.openfang/clips/script_packages/TIMESTAMP_My_Video/

# Step 6: Export for production
# (Choose option 6 from menu, select format)

# Step 7: Use in video production
# Import script_export.md into your video editor
```

---

## 📞 Support / 支持

**Issues:** GitHub Issues
**Discussions:** GitHub Discussions
**Documentation:** See "Further Reading" above

---

**Last Updated:** 2026-03-29
**Version:** 1.0
**Status:** ✅ Production Ready
