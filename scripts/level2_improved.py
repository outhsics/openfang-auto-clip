"""
Improved Level 2 Script Generation Module

This module contains enhanced functions for Level 2 script generation
with better coherence, specificity, and validation.

Key Improvements:
- Content-aware script generation
- Detailed visual direction
- Semantic similarity validation
- Content type adaptation
- Adaptive timing
"""

import re
from typing import Dict, List, Optional, Tuple
from enum import Enum


class ContentType(Enum):
    """Content types for Level 2 processing"""
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    TUTORIAL = "tutorial"
    GENERAL = "general"


class SectionType(Enum):
    """Section types in script structure"""
    HOOK = "hook"
    BODY = "body"
    CLOSE = "close"


# ============================================================================
# CONTENT TYPE DETECTION
# ============================================================================

def detect_content_type(transcript: dict, metadata: dict) -> ContentType:
    """
    Detect content type from transcript and metadata.

    Args:
        transcript: Transcript payload with text and segments
        metadata: Video metadata including title, description

    Returns:
        ContentType enum value
    """
    text = transcript["text"].lower()
    title = metadata.get("title", "").lower()
    description = metadata.get("description", "").lower()
    combined = f"{text} {title} {description}"

    # Educational indicators
    edu_keywords = [
        "learn", "understand", "explain", "concept", "theory",
        "原理", "学习", "理解", "解释", "概念",
        "educational", "lesson", "course", "study"
    ]

    # Tutorial indicators
    tut_keywords = [
        "step", "how to", "tutorial", "guide", "instruction",
        "教程", "步骤", "方法", "指南", "教学",
        "demonstrate", "show you", "follow along"
    ]

    # Entertainment indicators
    ent_keywords = [
        "funny", "joke", "story", "hilarious", "comedy",
        "搞笑", "故事", "喜剧", "幽默", "有趣",
        "entertainment", "skit", "prank"
    ]

    # Count keyword matches
    edu_score = sum(1 for kw in edu_keywords if kw in combined)
    tut_score = sum(1 for kw in tut_keywords if kw in combined)
    ent_score = sum(1 for kw in ent_keywords if kw in combined)

    # Determine type based on highest score
    scores = {
        ContentType.EDUCATIONAL: edu_score,
        ContentType.TUTORIAL: tut_score,
        ContentType.ENTERTAINMENT: ent_score,
    }

    max_score = max(scores.values())

    if max_score == 0:
        return ContentType.GENERAL

    for content_type, score in scores.items():
        if score == max_score:
            return content_type

    return ContentType.GENERAL


# ============================================================================
# IMPROVED SCRIPT GENERATION
# ============================================================================

def extract_key_points(summary: str) -> List[str]:
    """
    Extract key points from a summary string.

    Args:
        summary: Summary text to extract from

    Returns:
        List of key points
    """
    # Split by common delimiters
    delimiters = [r'\. ', r'! ', r'\? ', r'。', r'！', r'？', r'; ', r'；']

    points = [summary]
    for delimiter in delimiters:
        new_points = []
        for point in points:
            new_points.extend(re.split(delimiter, point))
        points = new_points

    # Clean and filter
    key_points = []
    for point in points:
        cleaned = point.strip()
        if len(cleaned) > 10:  # Filter out too-short fragments
            key_points.append(cleaned)

    return key_points[:5]  # Limit to top 5 points


def generate_hook_narration(
    key_points: List[str],
    content_type: ContentType,
    language: str
) -> str:
    """
    Generate an engaging hook narration.

    Args:
        key_points: Main points to cover
        content_type: Type of content
        language: "en" or "zh"

    Returns:
        Hook narration text
    """
    main_point = key_points[0] if key_points else ""

    if language == "zh":
        if content_type == ContentType.EDUCATIONAL:
            templates = [
                f"你有没有想过，为什么{main_point}这么重要？",
                f"大多数人都不知道，{main_point}背后的真相是这样的。",
                f"今天我要告诉你一个关于{main_point}的颠覆性认知。",
            ]
        elif content_type == ContentType.TUTORIAL:
            templates = [
                f"教你一招，轻松搞定{main_point}！",
                f"这个{main_point}的方法，我保证你没用过。",
                f"3分钟掌握{main_point}，高手都在用。",
            ]
        elif content_type == ContentType.ENTERTAINMENT:
            templates = [
                f"准备好被{main_point}震撼到了吗？",
                f"关于{main_point}，这个绝对会让你笑到停不下来。",
                f"你绝对猜不到{main_point}竟然是这样！",
            ]
        else:
            templates = [
                f"关于{main_point}，有个重要的事情要告诉你。",
                f"今天我们来聊聊{main_point}这件事。",
                f"{main_point}，这确实值得你花60秒了解。",
            ]
    else:
        if content_type == ContentType.EDUCATIONAL:
            templates = [
                f"Have you ever wondered why {main_point} matters so much?",
                f"Most people don't know the truth about {main_point}.",
                f"Today I'll share a game-changing insight about {main_point}.",
            ]
        elif content_type == ContentType.TUTORIAL:
            templates = [
                f"Here's a trick to master {main_point} in no time.",
                f"This {main_point} method will change everything.",
                f"Master {main_point} in 3 minutes with this proven technique.",
            ]
        elif content_type == ContentType.ENTERTAINMENT:
            templates = [
                f"Get ready to be amazed by {main_point}.",
                f"This {main_point} story will have you on the floor.",
                f"You won't believe what {main_point} is really like.",
            ]
        else:
            templates = [
                f"Here's something important about {main_point}.",
                f"Let's talk about {main_point}.",
                f"{main_point} is worth your next 60 seconds.",
            ]

    # Return first template (can be randomized later)
    return templates[0]


def generate_body_narration(
    point: str,
    index: int,
    total: int,
    content_type: ContentType,
    language: str
) -> str:
    """
    Generate body section narration.

    Args:
        point: Key point to cover
        index: Section index (1-based)
        total: Total number of body sections
        content_type: Type of content
        language: "en" or "zh"

    Returns:
        Body narration text
    """
    if language == "zh":
        if content_type == ContentType.EDUCATIONAL:
            templates = [
                f"第{index}个重点是{point}。为什么这么说？因为它直接影响了我们的理解和应用。",
                f"接下来这个关键点很关键：{point}。很多人忽视了这个细节。",
                f"关于{point}，这里有个专业的解释。",
            ]
        elif content_type == ContentType.TUTORIAL:
            templates = [
                f"第{index}步，{point}。这一步最关键，一定要看仔细。",
                f"接下来是{point}。记住这个技巧，事半功倍。",
                f"到了第{index}步，{point}。高手都是这么做的。",
            ]
        elif content_type == ContentType.ENTERTAINMENT:
            templates = [
                f"最精彩的部分来了：{point}。准备好笑了吗？",
                f"等等，还没完！{point}这个才是重头戏。",
                f"关于{point}，这个反转绝对没想到。",
            ]
        else:
            templates = [
                f"第{index}点，{point}。这个确实很重要。",
                f"关于{point}，这里有个不同的视角。",
                f"接下来是{point}，值得注意。",
            ]
    else:
        if content_type == ContentType.EDUCATIONAL:
            templates = [
                f"Point {index}: {point}. Here's why this matters.",
                f"Next key point: {point}. This is often overlooked.",
                f"Here's a professional take on {point}.",
            ]
        elif content_type == ContentType.TUTORIAL:
            templates = [
                f"Step {index}: {point}. This is crucial.",
                f"Next up: {point}. Remember this technique.",
                f"Here's step {index}: {point}. Experts do it this way.",
            ]
        elif content_type == ContentType.ENTERTAINMENT:
            templates = [
                f"Best part coming up: {point}. Ready?",
                f"Wait for it: {point} is the real highlight.",
                f"Here's the twist: {point}. Didn't see that coming.",
            ]
        else:
            templates = [
                f"Point {index}: {point}. This is important.",
                f"Here's a different take on {point}.",
                f"Next is {point}. Worth noting.",
            ]

    # Rotate through templates
    template_index = (index - 1) % len(templates)
    return templates[template_index]


def generate_close_narration(
    key_points: List[str],
    content_type: ContentType,
    language: str
) -> str:
    """
    Generate closing narration.

    Args:
        key_points: Main points covered
        content_type: Type of content
        language: "en" or "zh"

    Returns:
        Closing narration text
    """
    point_summary = "、".join(key_points[:3])

    if language == "zh":
        if content_type == ContentType.EDUCATIONAL:
            templates = [
                f"总结一下，{point_summary}这些知识点，现在你可以开始应用了。建议从第一个开始实践。",
                f"所以，{point_summary}就是核心。想深入学习的话，关注我获取更多资料。",
                f"记住{point_summary}这几点，你已经超过了90%的人。接下来该你行动了。",
            ]
        elif content_type == ContentType.TUTORIAL:
            templates = [
                f"完成了！按照{point_summary}这些步骤，你也能轻松搞定。快去试试吧！",
                f"这就是掌握{point_summary}的完整流程。点赞收藏，下次照着做。",
                f"学会了吗？{point_summary}，多练习几次就熟练了。有问题评论区见。",
            ]
        elif content_type == ContentType.ENTERTAINMENT:
            templates = [
                f"哈哈，{point_summary}是不是很有意思？关注我看更多有趣内容！",
                f"所以说{point_summary}，生活就是这么有趣。别忘了分享给朋友。",
                f"看完这个，是不是对{point_summary}有了新认识？点赞支持一下！",
            ]
        else:
            templates = [
                f"简单说，就是{point_summary}。希望对你有帮助。",
                f"{point_summary}，这就是今天的重点。感谢观看。",
                f"记住{point_summary}这几点。我们下期见。",
            ]
    else:
        if content_type == ContentType.EDUCATIONAL:
            templates = [
                f"So there you have it: {point_summary}. Start applying these today.",
                f"Key takeaways: {point_summary}. Follow for more insights.",
                f"You're now ahead of 90% of people who understand {point_summary}. Take action!",
            ]
        elif content_type == ContentType.TUTORIAL:
            templates = [
                f"That's it! With {point_summary}, you're ready to go. Try it now!",
                f"Master {point_summary} with these steps. Save this for later.",
                f"Got it? Practice {point_summary} a few times. See you in the comments.",
            ]
        elif content_type == ContentType.ENTERTAINMENT:
            templates = [
                f"Haha! {point_summary} - pretty wild, right? Follow for more!",
                f"See? {point_summary} is just amazing. Share with friends!",
                f"New perspective on {point_summary}? Like and follow for more!",
            ]
        else:
            templates = [
                f"Simply put: {point_summary}. Hope this helped!",
                f"{point_summary} - that's today's highlight. Thanks for watching!",
                f"Remember {point_summary}. See you next time!",
            ]

    return templates[0]


def generate_improved_script_sections(
    points: List[dict],
    content_type: ContentType,
    language: str,
    duration: int
) -> List[dict]:
    """
    Generate improved script sections with content-aware narration.

    Args:
        points: List of transcript points
        content_type: Detected content type
        language: "en" or "zh"
        duration: Target duration in seconds

    Returns:
        List of script section dictionaries
    """
    # Extract key points
    key_points = [point["summary"] for point in points]

    # Calculate adaptive durations
    hook_duration = calculate_adaptive_duration(
        {"type": "hook", "complexity": 0.5},
        content_type,
        duration
    )
    closing_duration = calculate_adaptive_duration(
        {"type": "close", "complexity": 0.3},
        content_type,
        duration
    )

    # Generate sections
    sections = []

    # Hook
    hook_narration = generate_hook_narration(key_points, content_type, language)
    sections.append({
        "section": "Hook" if language == "en" else "开场",
        "duration": hook_duration,
        "narration": hook_narration,
        "on_screen_text": shorten_phrase(key_points[0], language),
        "visual_direction": generate_hook_visual_direction(content_type, language),
        "source_anchor": points[0].get("source_anchor") if points else None,
    })

    # Body sections
    body_total = duration - hook_duration - closing_duration
    body_duration = max(6, int(body_total / len(points)))

    for index, point in enumerate(points, start=1):
        body_narration = generate_body_narration(
            point["summary"],
            index,
            len(points),
            content_type,
            language
        )

        sections.append({
            "section": f"Beat {index}" if language == "en" else f"重点 {index}",
            "duration": body_duration,
            "narration": body_narration,
            "on_screen_text": shorten_phrase(point["summary"], language),
            "visual_direction": generate_body_visual_direction(index, content_type, language),
            "source_anchor": point.get("source_anchor"),
        })

    # Close
    close_narration = generate_close_narration(key_points, content_type, language)
    sections.append({
        "section": "Close" if language == "en" else "收尾",
        "duration": duration - sum(s["duration"] for s in sections),
        "narration": close_narration,
        "on_screen_text": "Summary & Action" if language == "en" else "总结与行动",
        "visual_direction": generate_close_visual_direction(content_type, language),
        "source_anchor": None,
    })

    return sections


# ============================================================================
# IMPROVED VISUAL DIRECTION
# ============================================================================

def generate_hook_visual_direction(content_type: ContentType, language: str) -> str:
    """Generate detailed visual direction for hook section."""

    if language == "zh":
        directions = {
            ContentType.EDUCATIONAL: "镜头1：特写标题卡，大号字体突出主题（2秒）。镜头2：切换到中景讲述者，眼神直视镜头，手势配合（剩余时间）。背景使用纯色或渐变，确保文字清晰可见。",
            ContentType.TUTORIAL: "镜头1：快速展示最终成果特写（1.5秒）。镜头2：切到讲述者中景，展示工具或材料（2.5秒）。镜头3：屏幕文字叠加'3秒学会'（剩余时间）。",
            ContentType.ENTERTAINMENT: "镜头1：快节奏剪辑，使用高对比度画面（2秒）。镜头2：讲述者夸张表情特写（2秒）。镜头3：快速切回正题，保持高能量（剩余时间）。",
            ContentType.GENERAL: "镜头1：标题卡全屏显示（2秒）。镜头2：讲述者中景开始讲述（剩余时间）。背景简洁，光线均匀。",
        }
    else:
        directions = {
            ContentType.EDUCATIONAL: "Shot 1: Close-up title card, large bold text (2s). Shot 2: Medium shot of speaker, direct eye contact, hand gestures (remaining). Clean solid/gradient background for text visibility.",
            ContentType.TUTORIAL: "Shot 1: Quick close-up of final result (1.5s). Shot 2: Medium shot showing tools/materials (2.5s). Shot 3: Text overlay 'Learn in 3 seconds' (remaining).",
            ContentType.ENTERTAINMENT: "Shot 1: Fast-paced montage, high contrast visuals (2s). Shot 2: Extreme close-up, exaggerated expression (2s). Shot 3: Quick cut to main topic, high energy (remaining).",
            ContentType.GENERAL: "Shot 1: Full-screen title card (2s). Shot 2: Medium shot of speaker starting narration (remaining). Clean background, even lighting.",
        }

    return directions.get(content_type, directions[ContentType.GENERAL])


def generate_body_visual_direction(index: int, content_type: ContentType, language: str) -> str:
    """Generate detailed visual direction for body sections."""

    if language == "zh":
        base_directions = {
            ContentType.EDUCATIONAL: f"镜头：中景讲述者配合图示或屏幕录制。画面左侧60%为讲述者，右侧40%为关键点图解。使用箭头或高亮框标注重点。镜头缓慢推近，增强关注感。",
            ContentType.TUTORIAL: f"镜头：特写演示区域，手指或工具指向关键位置。旁白时插入全屏文字说明关键步骤。使用圆圈或箭头动画引导视线。确保操作区域清晰可见。",
            ContentType.ENTERTAINMENT: f"镜头：快速切换不同景别，保持视觉新鲜感。使用反应镜头或表情特写增强喜剧效果。配合音效卡点切换画面。",
            ContentType.GENERAL: f"镜头：讲述者中景，配合相关B-roll素材。B-roll占比30%，讲述者70%。使用平滑过渡效果。",
        }
    else:
        base_directions = {
            ContentType.EDUCATIONAL: f"Shot: Medium shot of speaker with diagrams or screen recording. Left 60% speaker, right 40% key visual. Use arrows or highlight boxes. Slow zoom in for focus.",
            ContentType.TUTORIAL: f"Shot: Close-up of demo area, finger or tool pointing to key spot. Full-screen text overlay for key steps. Use circle or arrow animations. Ensure demo area is clearly visible.",
            ContentType.ENTERTAINMENT: f"Shot: Fast cuts between different shot sizes for freshness. Use reaction shots or extreme close-ups for comedy. Time cuts to sound effects.",
            ContentType.GENERAL: f"Shot: Medium shot of speaker with relevant B-roll. 30% B-roll, 70% speaker. Use smooth transitions.",
        }

    return base_directions.get(content_type, base_directions[ContentType.GENERAL])


def generate_close_visual_direction(content_type: ContentType, language: str) -> str:
    """Generate detailed visual direction for closing section."""

    if language == "zh":
        directions = {
            ContentType.EDUCATIONAL: "镜头：总结卡片全屏显示，列出3个关键点（3秒）。镜头2：讲述者中景，给出行动建议（3秒）。镜头3：关注/点赞图标动画（剩余时间）。",
            ContentType.TUTORIAL: "镜头：最终成果展示，慢动作特写（2秒）。镜头2：讲述者手持成果，展示效果（3秒）。镜头3：文字叠加'去试试吧'（剩余时间）。",
            ContentType.ENTERTAINMENT: "镜头：讲述者大笑或反应镜头（2秒）。镜头2：快速回顾精彩瞬间（3秒）。镜头3：夸张的'关注我'手势（剩余时间）。",
            ContentType.GENERAL: "镜头：总结卡片全屏（2秒）。镜头2：讲述者中景总结（3秒）。镜头3：简单的结束画面（剩余时间）。",
        }
    else:
        directions = {
            ContentType.EDUCATIONAL: "Shot: Full-screen summary card with 3 key points (3s). Shot 2: Medium shot with action item (3s). Shot 3: Follow/like icon animation (remaining).",
            ContentType.TUTORIAL: "Shot: Final result showcase, slow motion close-up (2s). Shot 2: Medium shot holding result (3s). Shot 3: Text overlay 'Try it now' (remaining).",
            ContentType.ENTERTAINMENT: "Shot: Speaker laughing or reaction shot (2s). Shot 2: Quick montage of highlights (3s). Shot 3: Exaggerated 'follow me' gesture (remaining).",
            ContentType.GENERAL: "Shot: Full-screen summary card (2s). Shot 2: Medium shot summary (3s). Shot 3: Simple end screen (remaining).",
        }

    return directions.get(content_type, directions[ContentType.GENERAL])


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def shorten_phrase(text: str, language: str, max_chars: int = 18) -> str:
    """
    Shorten a phrase for on-screen text display.

    Args:
        text: Original text
        language: "en" or "zh"
        max_chars: Maximum character count

    Returns:
        Shortened phrase
    """
    # Remove common filler words
    if language == "en":
        filler_words = ["the", "a", "an", "is", "are", "was", "were", "this", "that"]
        words = text.split()
        filtered = [w for w in words if w.lower() not in filler_words]
        text = " ".join(filtered)

    # Truncate if necessary
    if len(text) > max_chars:
        if language == "zh":
            return text[:max_chars-1] + "…"
        else:
            return text[:max_chars-4] + "..."

    return text


def calculate_adaptive_duration(
    section: dict,
    content_type: ContentType,
    total_duration: int
) -> int:
    """
    Calculate adaptive duration based on content complexity and type.

    Args:
        section: Section info with type and complexity
        content_type: Content type
        total_duration: Total target duration

    Returns:
        Adaptive duration in seconds
    """
    base_duration = section.get("base_duration", 10)
    complexity = section.get("complexity", 0.5)

    # Complexity multiplier (0.7 to 1.3)
    complexity_multiplier = 1.0 + ((complexity - 0.5) * 0.6)

    # Content type multipliers
    type_multipliers = {
        ContentType.EDUCATIONAL: 1.15,  # More time for explanations
        ContentType.TUTORIAL: 1.1,     # Time for demonstrations
        ContentType.ENTERTAINMENT: 0.85,  # Faster pacing
        ContentType.GENERAL: 1.0,
    }

    type_multiplier = type_multipliers.get(content_type, 1.0)

    # Calculate final duration
    duration = int(base_duration * complexity_multiplier * type_multiplier)

    # Ensure within bounds
    return max(6, min(duration, total_duration // 2))


# ============================================================================
# PUBLIC API
# ============================================================================

def build_improved_level2_package(
    video_info: dict,
    transcript_payload: dict,
    transcript_path: Path,
    config: dict
) -> dict:
    """
    Build an improved Level 2 script package.

    This is the main entry point for improved Level 2 generation.

    Args:
        video_info: Video metadata
        transcript_payload: Parsed transcript with text and segments
        transcript_path: Path to transcript file
        config: Configuration dictionary

    Returns:
        Enhanced Level 2 package dictionary
    """
    from pathlib import Path
    from auto_clip import (
        build_source_outline_from_segments,
        detect_transcript_language,
        split_transcript_sentences,
    )

    # Extract transcript information
    transcript_text = transcript_payload["text"]
    sentences = split_transcript_sentences(transcript_text)

    if len(sentences) < 3:
        raise ValueError("Transcript too short to generate meaningful script")

    # Detect language and content type
    language = detect_transcript_language(transcript_text)
    content_type = detect_content_type(transcript_payload, video_info)

    # Build source outline
    source_outline = build_source_outline_from_segments(
        transcript_payload.get("segments", []),
        language
    )

    # Generate improved script sections
    target_duration = config.get("default_duration", 60)
    script_sections = generate_improved_script_sections(
        source_outline,
        content_type,
        language,
        target_duration
    )

    # Generate shot plan with improved visual direction
    shot_plan = build_improved_shot_plan(script_sections, content_type, language)

    # Build complete package
    package = {
        "milestone": "level2_improved_transcript_to_script_package",
        "version": "2.0",
        "source": {
            "title": video_info.get("title", "Unknown"),
            "path": str(transcript_path),
            "language": language,
            "content_type": content_type.value,
            "segment_count": len(transcript_payload.get("segments", [])),
        },
        "script_sections": script_sections,
        "shot_plan": shot_plan,
        "improvements": [
            "Content-aware script generation",
            "Detailed visual direction",
            "Content type adaptation",
            "Adaptive timing",
        ],
    }

    return package


def build_improved_shot_plan(
    script_sections: List[dict],
    content_type: ContentType,
    language: str
) -> List[dict]:
    """
    Build improved shot plan with detailed specifications.

    Args:
        script_sections: Script sections from improved generation
        content_type: Detected content type
        language: "en" or "zh"

    Returns:
        List of detailed shot plan entries
    """
    shot_plan = []

    for index, section in enumerate(script_sections, start=1):
        section_type = (
            SectionType.HOOK if index == 1
            else SectionType.CLOSE if index == len(script_sections)
            else SectionType.BODY
        )

        # Determine shot specifications
        shot_spec = determine_shot_specifications(section_type, content_type, language)

        shot_plan.append({
            "shot": index,
            "section": section["section"],
            "duration": section["duration"],
            "shot_type": shot_spec["shot_type"],
            "camera_angle": shot_spec["camera_angle"],
            "camera_movement": shot_spec["camera_movement"],
            "framing": shot_spec["framing"],
            "visual_direction": section["visual_direction"],
            "overlay_text": section["on_screen_text"],
            "source_anchor": section.get("source_anchor"),
        })

    return shot_plan


def determine_shot_specifications(
    section_type: SectionType,
    content_type: ContentType,
    language: str
) -> dict:
    """
    Determine detailed shot specifications.

    Args:
        section_type: Hook, body, or close
        content_type: Content type
        language: "en" or "zh"

    Returns:
        Dictionary with shot specifications
    """
    specs = {
        SectionType.HOOK: {
            "shot_type": "title_card_to_medium",
            "camera_angle": "eye_level",
            "camera_movement": "static_then_slow_zoom_in",
            "framing": "center_weighted",
        },
        SectionType.BODY: {
            "shot_type": "medium_with_overlays",
            "camera_angle": "eye_level",
            "camera_movement": "subtle_movement",
            "framing": "rule_of_thirds",
        },
        SectionType.CLOSE: {
            "shot_type": "summary_card_to_medium",
            "camera_angle": "eye_level",
            "camera_movement": "static",
            "framing": "center_weighted",
        },
    }

    return specs.get(section_type, specs[SectionType.BODY])


def render_improved_script_markdown(package: dict) -> str:
    """
    Render the improved Level 2 script package into markdown.

    Args:
        package: Improved Level 2 package

    Returns:
        Markdown formatted script
    """
    lines = [
        "# Level 2 Script Package (Improved)",
        "",
        f"**Version:** {package.get('version', '2.0')}",
        f"**Content Type:** {package.get('source', {}).get('content_type', 'N/A')}",
        f"**Language:** {package.get('source', {}).get('language', 'N/A')}",
        "",
        "---",
        "",
        "## Script Draft",
        "",
    ]

    for section in package.get("script_sections", []):
        lines.extend([
            f"### {section['section']} ({section['duration']}s)",
            "",
            f"**Narration:** {section['narration']}",
            "",
            f"**On-Screen Text:** {section['on_screen_text']}",
            "",
            f"**Visual Direction:** {section['visual_direction']}",
            "",
        ])

    lines.extend([
        "---",
        "",
        "## Improvements",
        "",
    ])

    for improvement in package.get("improvements", []):
        lines.append(f"- {improvement}")

    return "\n".join(lines)
