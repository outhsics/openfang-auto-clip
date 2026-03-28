# Level 2 Implementation Analysis & Improvement Plan

**Date:** 2026-03-28
**Phase:** Phase 1 Week 2
**Status:** 🟡 Analysis Complete

---

## 🔍 Current Implementation Analysis

### Core Functions Analyzed

1. **`build_level2_script_sections()`** - Generates script sections
2. **`build_level2_shot_plan()`** - Creates visual direction
3. **`build_level2_asset_requests()`** - Defines asset needs
4. **`build_level2_voiceover_notes()`** - Voiceover guidance

---

## ❌ Identified Issues

### 1. Script Coherence Problems / 脚本连贯性问题

**Issue:** Template-based narration doesn't actually rewrite content

**Current Code:**
```python
# English
"narration": f"Retell the core idea from a fresh angle: {points[0]['summary']}."

# Chinese
"narration": f"这条短视频不用原句复述，先用新的讲法讲清核心点：{points[0]['summary']}。"
```

**Problems:**
- ❌ Directly embeds original `summary` without rewriting
- ❌ Template is generic, doesn't adapt to content
- ❌ No actual "fresh angle" - just instruction to create one
- ❌ Same template for all content types

**Impact:**
- Low originality scores
- High copyright risk
- Poor user satisfaction
- Requires manual revision

---

### 2. Visual Direction Too Vague / 视觉指导不够具体

**Issue:** Shot plans lack specific details

**Current Code:**
```python
asset_type = "title_card_then_new_talking_head"
goal_en = "State the new angle quickly and clearly."
```

**Problems:**
- ❌ No camera angle specification
- ❌ No movement direction
- ❌ No framing details
- ❌ No lighting guidance
- ❌ Asset types are too generic

**What's Missing:**
- Specific shot types (close-up, medium, wide, etc.)
- Camera movements (pan, tilt, zoom, etc.)
- Transition types
- Color grading guidance
- Text placement specifics

**Impact:**
- Low actionability scores
- Editors can't execute without clarification
- Inconsistent visual quality

---

### 3. No Content Validation / 缺乏内容验证

**Issue:** No checks for quality, similarity, or value retention

**Missing Validations:**
- ❌ No semantic similarity check
- ❌ No key point retention verification
- ❌ No copyright risk assessment
- ❌ No quality scoring
- ❌ No length validation

**Impact:**
- Can't guarantee quality
- Risk of losing core message
- Potential copyright issues
- No objective quality metrics

---

### 4. Lack of Content Type Adaptation / 缺乏内容类型适配

**Issue:** One-size-fits-all approach

**Current Behavior:**
- Same script structure for educational, entertainment, tutorial
- Same visual style regardless of content
- No tone adaptation

**What Should Vary:**
- **Educational:** Clear explanations, diagrams, examples
- **Entertainment:** Energetic, dynamic, humor
- **Tutorial:** Step-by-step, clear demonstrations
- **Business:** Professional, data-driven, authoritative

**Impact:**
- Generic output
- Doesn't match audience expectations
- Lower engagement potential

---

### 5. Timing Issues / 时序问题

**Issue:** Duration calculation is rigid

**Current Code:**
```python
hook_duration = max(6, int(duration * 0.2))
body_duration = max(6, int(body_total / max(len(points), 1)))
```

**Problems:**
- ❌ Fixed percentages don't adapt to content
- ❌ No consideration of content complexity
- ❌ Minimum durations may be too short/long
- ❌ No pacing variation

**Impact:**
- Rushed or dragged sections
- Poor pacing
- Lower engagement

---

## ✅ Improvement Plan

### Priority 1: Script Coherence / 脚本连贯性

#### 1.1 Content-Aware Script Generation

**Approach:** Generate actual rewritten content instead of templates

**Implementation:**
```python
def generate_section_narration(point: dict, section_type: str, content_type: str, language: str) -> str:
    """Generate section-specific narration based on content type."""

    # Extract key information
    key_points = extract_key_points(point['summary'])

    # Apply content-specific transformations
    if content_type == "educational":
        narration = generate_educational_narration(key_points, section_type, language)
    elif content_type == "entertainment":
        narration = generate_entertainment_narration(key_points, section_type, language)
    elif content_type == "tutorial":
        narration = generate_tutorial_narration(key_points, section_type, language)
    else:
        narration = generate_generic_narration(key_points, section_type, language)

    return narration
```

**Benefits:**
- ✅ Actual content rewriting
- ✅ Content-type aware
- ✅ Higher originality
- ✅ Better engagement

---

#### 1.2 Improved Transitions

**Approach:** Add smooth transitions between sections

**Implementation:**
```python
TRANSITION_TEMPLATES = {
    "hook_to_body": [
        "Here's why this matters: {connection}",
        "Let me show you exactly how: {connection}",
        "The key insight is this: {connection}",
    ],
    "body_to_body": [
        "Building on that, {next_point}",
        "But here's the thing: {next_point}",
        "Now, here's what's interesting: {next_point}",
    ],
    "body_to_close": [
        "So what does this all mean? {takeaway}",
        "Putting it all together: {takeaway}",
        "Here's your action plan: {takeaway}",
    ],
}
```

**Benefits:**
- ✅ Smoother flow
- ✅ Better coherence
- ✅ Higher quality scores

---

### Priority 2: Visual Direction Specificity / 视觉指导具体性

#### 2.1 Detailed Shot Specifications

**Approach:** Add comprehensive shot details

**Implementation:**
```python
def generate_detailed_shot_plan(section: dict, content_type: str, language: str) -> dict:
    """Generate detailed shot specifications."""

    shot_details = {
        "shot_type": determine_shot_type(section, content_type),
        "camera_angle": determine_camera_angle(section),
        "camera_movement": determine_camera_movement(section),
        "framing": determine_framing(section),
        "lighting": determine_lighting(content_type),
        "color_grading": determine_color_grading(content_type),
        "transition": determine_transition(section),
        "text_placement": determine_text_placement(section),
        "overlay_specs": determine_overlay_specs(section),
    }

    return shot_details
```

**Benefits:**
- ✅ Actionable instructions
- ✅ Consistent quality
- ✅ Higher actionability scores

---

#### 2.2 Content-Specific Visual Styles

**Approach:** Define visual styles for each content type

**Implementation:**
```python
VISUAL_STYLES = {
    "educational": {
        "primary": "talking_head_with_diagrams",
        "secondary": "screen_recording",
        "color_scheme": "professional_blue",
        "text_style": "clean_minimal",
    },
    "entertainment": {
        "primary": "dynamic_broll",
        "secondary": "reaction_shots",
        "color_scheme": "vibrant_high_contrast",
        "text_style": "bold_attention_grabbing",
    },
    "tutorial": {
        "primary": "screen_recording",
        "secondary": "close_up_demonstration",
        "color_scheme": "clear_high_visibility",
        "text_style": "instructional_step_by_step",
    },
}
```

**Benefits:**
- ✅ Matches content expectations
- ✅ Better audience engagement
- ✅ Professional results

---

### Priority 3: Content Validation / 内容验证

#### 3.1 Semantic Similarity Check

**Approach:** Verify originality while maintaining value

**Implementation:**
```python
def check_semantic_similarity(original_text: str, new_text: str, threshold: float = 0.7) -> dict:
    """Check semantic similarity using embeddings."""

    # Generate embeddings
    original_emb = get_embedding(original_text)
    new_emb = get_embedding(new_text)

    # Calculate similarity
    similarity = cosine_similarity(original_emb, new_emb)

    return {
        "similarity_score": similarity,
        "is_too_similar": similarity > threshold,
        "recommendation": "revise" if similarity > threshold else "approve",
    }
```

**Benefits:**
- ✅ Objective quality measure
- ✅ Copyright risk detection
- ✅ Consistent standards

---

#### 3.2 Key Point Retention Check

**Approach:** Ensure core message is preserved

**Implementation:**
```python
def check_key_point_retention(original_points: List[str], new_script: str) -> dict:
    """Verify key points are retained in new script."""

    retained = []
    lost = []

    for point in original_points:
        if similar_concept_exists(point, new_script):
            retained.append(point)
        else:
            lost.append(point)

    return {
        "retention_rate": len(retained) / len(original_points),
        "retained_points": retained,
        "lost_points": lost,
        "is_acceptable": len(retained) / len(original_points) >= 0.8,
    }
```

**Benefits:**
- ✅ Value preservation
- ✅ Quality assurance
- ✅ User confidence

---

#### 3.3 Quality Scoring System

**Approach:** Multi-dimensional quality assessment

**Implementation:**
```python
def calculate_quality_score(package: dict) -> dict:
    """Calculate overall quality score."""

    scores = {
        "coherence": score_coherence(package),
        "actionability": score_actionability(package),
        "originality": score_originality(package),
        "value_retention": score_value_retention(package),
    }

    overall = sum(scores.values()) / len(scores)

    return {
        "scores": scores,
        "overall": overall,
        "is_production_ready": overall >= 8.0,
        "is_acceptable": overall >= 6.0,
    }
```

**Benefits:**
- ✅ Objective metrics
- ✅ Consistent evaluation
- ✅ Clear improvement targets

---

### Priority 4: Content Type Adaptation / 内容类型适配

#### 4.1 Content Type Detection

**Approach:** Automatically detect content type

**Implementation:**
```python
def detect_content_type(transcript: dict, metadata: dict) -> str:
    """Detect content type from transcript and metadata."""

    text = transcript["text"].lower()
    title = metadata.get("title", "").lower()

    # Check for educational indicators
    if any(word in text for word in ["learn", "understand", "explain", "concept", "原理", "学习"]):
        return "educational"

    # Check for tutorial indicators
    if any(word in text for word in ["step", "how to", "tutorial", "guide", "教程", "步骤"]):
        return "tutorial"

    # Check for entertainment indicators
    if any(word in text for word in ["funny", "joke", "story", "hilarious", "搞笑", "故事"]):
        return "entertainment"

    return "general"
```

**Benefits:**
- ✅ Automatic adaptation
- ✅ Better targeting
- ✅ Higher engagement

---

#### 4.2 Adaptive Script Structures

**Approach:** Different structures for different types

**Implementation:**
```python
SCRIPT_STRUCTURES = {
    "educational": {
        "sections": ["hook", "concept_intro", "explanation_1", "example_1", "explanation_2", "key_takeaway", "action_item"],
        "tone": "informative_clear",
        "pacing": "moderate_steady",
    },
    "entertainment": {
        "sections": ["hook", "setup", "punchline_1", "punchline_2", "callback", "call_to_action"],
        "tone": "energetic_dynamic",
        "pacing": "fast_snappy",
    },
    "tutorial": {
        "sections": ["hook", "overview", "step_1", "step_2", "step_3", "tips", "final_result"],
        "tone": "instructional_patient",
        "pacing": "moderate_demonstration",
    },
}
```

**Benefits:**
- ✅ Type-appropriate structure
- ✅ Better audience fit
- ✅ Higher satisfaction

---

### Priority 5: Adaptive Timing / 自适应时序

#### 5.1 Content-Aware Duration

**Approach:** Adjust timing based on content complexity

**Implementation:**
```python
def calculate_adaptive_duration(section: dict, content_type: str, total_duration: int) -> int:
    """Calculate duration based on content complexity."""

    base_duration = section.get("base_duration", 10)

    # Adjust for complexity
    complexity = calculate_complexity(section)
    complexity_multiplier = 1.0 + (complexity * 0.3)

    # Adjust for content type
    type_multipliers = {
        "educational": 1.2,  # More time for explanations
        "entertainment": 0.8,  # Faster pacing
        "tutorial": 1.1,  # Time for steps
        "general": 1.0,
    }

    type_multiplier = type_multipliers.get(content_type, 1.0)

    # Calculate final duration
    duration = int(base_duration * complexity_multiplier * type_multiplier)

    # Ensure within bounds
    return max(6, min(duration, total_duration // 2))
```

**Benefits:**
- ✅ Better pacing
- ✅ Content-appropriate
- ✅ Higher engagement

---

## 📊 Expected Improvements

### Quality Score Targets

| Dimension | Current | Target | Improvement |
|-----------|---------|--------|-------------|
| Coherence | 5/10 | 8/10 | +60% |
| Actionability | 5/10 | 8/10 | +60% |
| Originality | 6/10 | 9/10 | +50% |
| Overall | 5.5/10 | 8.5/10 | +55% |

### User Experience Improvements

- ✅ Less manual revision needed
- ✅ Higher satisfaction
- ✅ Faster production time
- ✅ Better final output

---

## 🎯 Implementation Order

### Week 2 (Current)
1. ✅ Analysis (Complete)
2. 🔄 Implement Priority 1 (Script Coherence)
3. 🔄 Implement Priority 2 (Visual Direction)

### Week 3
4. Implement Priority 3 (Content Validation)
5. Implement Priority 4 (Content Type Adaptation)
6. Implement Priority 5 (Adaptive Timing)

### Week 4-5
7. Testing and refinement
8. Before/after comparison
9. Quality validation

---

## 📝 Next Steps

1. ✅ Analysis complete
2. 🔄 Create improved implementation
3. 🔄 Generate before/after samples
4. 🔄 Run quality tests
5. 🔄 Document improvements

---

**Last Updated:** 2026-03-28
**Status:** 🟡 Ready for Implementation
**Next:** Create improved Level 2 functions
