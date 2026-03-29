# OpenFang Template Gallery

Community-contributed templates for different video types and platforms.

---

## 📋 What are Templates?

Templates are pre-configured scripts and styles for common video types. They provide:

- **Structure**: Proven video organization
- **Timing**: Optimized durations for each section
- **Style**: Visual and audio guidelines
- **Best Practices**: Platform-specific optimization

---

## 🎯 Available Templates

### 1. YouTube Intro (`youtube_intro.json`)

**Best for**: Channel branding and introductions

**Duration**: 30 seconds

**Sections**:
- Hook (3s) - Grab attention
- Intro (5s) - Channel branding
- Main Content (17s) - Core message
- Outro (5s) - Call to action

**Use when**:
- Creating channel intros
- Establishing brand identity
- Professional YouTube content

---

### 2. TikTok Trend (`tiktok_trend.json`)

**Best for**: Viral short-form content

**Duration**: 15 seconds

**Sections**:
- Hook (2s) - Instant attention
- Trend Setup (3s) - Establish context
- Main Content (7s) - Core content
- Call to Action (3s) - Drive engagement

**Use when**:
- Creating viral TikTok content
- Jumping on trends
- Maximizing engagement

---

### 3. Tutorial (`tutorial.json`)

**Best for**: Teaching skills and concepts

**Duration**: 60 seconds

**Sections**:
- Intro (10s) - Set expectations
- Overview (5s) - Show end result
- Step Demonstration (35s) - Teach step-by-step
- Summary (10s) - Reinforce learning

**Use when**:
- Teaching how-to content
- Explaining processes
- Creating educational videos

---

### 4. Educational Content (`educational.json`)

**Best for**: Explaining concepts and ideas

**Duration**: 90 seconds

**Sections**:
- Hook (10s) - Capture interest
- Context (15s) - Provide background
- Explanation (45s) - Core content
- Examples (15s) - Real-world application
- Summary (5s) - Key takeaways

**Use when**:
- Explaining complex topics
- Teaching concepts
- Creating educational content

---

## 🚀 How to Use Templates

### Option 1: CLI

```bash
# Use a template
auto_clip process transcript.srt --template examples/templates/youtube_intro.json

# List available templates
auto_clip templates --list

# Preview a template
auto_clip templates --preview youtube_intro
```

### Option 2: Python SDK

```python
from openfang_sdk import Client
import json

client = Client()

# Load template
with open('examples/templates/youtube_intro.json') as f:
    template = json.load(f)

# Process with template
job = client.process(
    transcript_path='transcript.srt',
    template=template
)

result = client.wait_for_job(job['job_id'])
```

### Option 3: Web Dashboard

1. Navigate to the Process page
2. Select "Use Template"
3. Choose a template from the dropdown
4. Customize as needed
5. Process your content

---

## 🎨 Creating Your Own Templates

### Template Structure

```json
{
  "template_name": "Your Template Name",
  "template_id": "unique_id_v1",
  "description": "Brief description",
  "version": "1.0.0",
  "author": "Your Name",

  "target_platform": "youtube|tiktok|instagram",
  "target_duration": 60,
  "content_type": "educational|entertainment|tutorial",

  "script_structure": {
    "section1_duration": 10,
    "section2_duration": 20
  },

  "script_sections": [
    {
      "section": "section_name",
      "duration": 10,
      "purpose": "Why this section exists",
      "content": "What content goes here",
      "visual": "Visual guidelines",
      "audio": "Audio guidelines"
    }
  ],

  "style_guidelines": {
    "tone": "professional|casual|friendly",
    "pacing": "fast|moderate|slow",
    "language_level": "beginner|intermediate|advanced"
  },

  "technical_specs": {
    "aspect_ratio": "16:9|9:16|1:1",
    "resolution": "1080p",
    "frame_rate": 30
  }
}
```

### Template Best Practices

1. **Start with Purpose**: What problem does this template solve?
2. **Test Thoroughly**: Verify timing and flow work well
3. **Provide Examples**: Include example prompts
4. **Document Well**: Explain each section clearly
5. **Version Control**: Use semantic versioning

### Submitting Your Template

1. Create your template JSON file
2. Test it with real content
3. Add documentation and examples
4. Submit a PR to the `examples/templates/` directory

---

## 📊 Template Comparison

| Template | Duration | Platform | Best For |
|----------|----------|----------|----------|
| YouTube Intro | 30s | YouTube | Branding |
| TikTok Trend | 15s | TikTok | Virality |
| Tutorial | 60s | YouTube | Teaching |
| Educational | 90s | YouTube | Learning |

---

## 🔧 Customization Tips

### Adjust Duration

```json
{
  "target_duration": 45,  // Change from default
  "script_structure": {
    "section1_duration": 8,  // Adjust proportions
    "section2_duration": 12
  }
}
```

### Change Platform

```json
{
  "target_platform": "instagram",  // Switch from YouTube
  "technical_specs": {
    "aspect_ratio": "1:1"  // Square for Instagram
  }
}
```

### Modify Style

```json
{
  "visual_style": {
    "color_scheme": "minimal",  // Your preference
    "transition_style": "fade"
  },
  "style_guidelines": {
    "tone": "casual",  // Match your brand
    "pacing": "fast"
  }
}
```

---

## 🤝 Contributing Templates

We welcome community contributions!

### What We're Looking For

- **Platform-specific templates**: Instagram Reels, YouTube Shorts, etc.
- **Industry templates**: Real estate, fitness, cooking, etc.
- **Style templates**: Minimal, bold, cinematic, etc.
- **Language templates**: Different languages and regions

### Submission Guidelines

1. **Test your template**: Use it with real content first
2. **Document well**: Explain when to use it
3. **Provide examples**: Include example prompts
4. **Follow the structure**: Use the template schema
5. **Version appropriately**: Start with v1.0.0

### Submit

1. Fork the repository
2. Add your template to `examples/templates/`
3. Update this README with your template
4. Submit a pull request

---

## 📚 Additional Resources

- [Template Schema Documentation](../docs/TEMPLATE_SCHEMA.md)
- [Creating Custom Templates](../docs/CREATING_TEMPLATES.md)
- [Template Examples Gallery](https://github.com/outhsics/openfang-auto-clip/issues?q=label%3Atemplate)

---

## 💬 Template Requests

Have an idea for a template but don't want to create it yourself?

1. **Check existing templates**: Make sure it doesn't exist
2. **Search issues**: See if someone already requested it
3. **Create an issue**: Use the "template" label
4. **Provide details**:
   - What platform?
   - What duration?
   - What use case?
   - Any specific requirements?

---

## 🎉 Acknowledgments

Thanks to all community members who contribute templates!

**Featured Contributors**:
- @username - YouTube Intro template
- @username - TikTok Trend template
- @username - Tutorial template
- @username - Educational template

---

**Last Updated**: 2026-03-29
**Template Count**: 4
**Version**: 1.0.0
