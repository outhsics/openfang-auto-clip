"""
Level 2 Content Validation Module

This module provides validation and quality scoring for Level 2 script packages.

Features:
- Semantic similarity checking
- Key point retention validation
- Quality scoring system
- Copyright risk assessment
"""

import re
import json
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from datetime import datetime


# ============================================================================
# SEMANTIC SIMILARITY CHECK
# ============================================================================

def check_semantic_similarity(
    original_text: str,
    new_text: str,
    threshold: float = 0.75
) -> Dict:
    """
    Check semantic similarity between original and new text.

    Uses word overlap and sequence matching as a proxy for semantic similarity.
    For production, consider using embeddings (OpenAI, Sentence-Transformers).

    Args:
        original_text: Original transcript text
        new_text: Generated script text
        threshold: Similarity threshold (0-1)

    Returns:
        Dictionary with similarity score and recommendation
    """
    # Normalize texts
    original_words = set(re.findall(r'\w+', original_text.lower()))
    new_words = set(re.findall(r'\w+', new_text.lower()))

    if not original_words or not new_words:
        return {
            "similarity_score": 0.0,
            "is_too_similar": False,
            "recommendation": "approve",
            "method": "word_overlap",
        }

    # Calculate Jaccard similarity
    intersection = original_words & new_words
    union = original_words | new_words
    jaccard = len(intersection) / len(union) if union else 0

    # Calculate word overlap ratio
    overlap_ratio = len(intersection) / len(original_words)

    # Combined score
    similarity_score = (jaccard * 0.6) + (overlap_ratio * 0.4)

    # Determine recommendation
    is_too_similar = similarity_score > threshold
    recommendation = "revise" if is_too_similar else "approve"

    return {
        "similarity_score": round(similarity_score, 3),
        "is_too_similar": is_too_similar,
        "recommendation": recommendation,
        "threshold": threshold,
        "method": "word_overlap_jaccard",
        "details": {
            "jaccard_similarity": round(jaccard, 3),
            "overlap_ratio": round(overlap_ratio, 3),
            "original_word_count": len(original_words),
            "new_word_count": len(new_words),
            "shared_words": len(intersection),
        }
    }


def check_section_similarity(
    original_summary: str,
    new_narration: str,
    threshold: float = 0.7
) -> Dict:
    """
    Check similarity for a single section.

    Args:
        original_summary: Original point summary
        new_narration: Generated narration
        threshold: Similarity threshold

    Returns:
        Similarity check result
    """
    result = check_semantic_similarity(original_summary, new_narration, threshold)

    # Add section-specific analysis
    original_phrases = extract_phrases(original_summary)
    new_phrases = extract_phrases(new_narration)

    exact_matches = sum(1 for p in original_phrases if p in new_phrases)
    phrase_match_ratio = exact_matches / len(original_phrases) if original_phrases else 0

    result["phrase_analysis"] = {
        "original_phrases": len(original_phrases),
        "exact_matches": exact_matches,
        "match_ratio": round(phrase_match_ratio, 3),
    }

    # Update recommendation if too many exact phrase matches
    if phrase_match_ratio > 0.5:
        result["recommendation"] = "revise"
        result["is_too_similar"] = True

    return result


def extract_phrases(text: str, min_length: int = 3) -> List[str]:
    """
    Extract meaningful phrases from text.

    Args:
        text: Input text
        min_length: Minimum phrase length

    Returns:
        List of phrases
    """
    # Split by common delimiters
    phrases = re.split(r'[.,;!?，。！？；]', text)

    # Filter and clean
    meaningful = []
    for phrase in phrases:
        cleaned = phrase.strip().lower()
        words = cleaned.split()
        if len(words) >= min_length:
            meaningful.append(cleaned)

    return meaningful


# ============================================================================
# KEY POINT RETENTION CHECK
# ============================================================================

def check_key_point_retention(
    original_points: List[str],
    new_script: str,
    min_retention: float = 0.8
) -> Dict:
    """
    Verify that key points from original are retained in new script.

    Args:
        original_points: List of original key points
        new_script: Generated script text
        min_retention: Minimum retention ratio (0-1)

    Returns:
        Retention check result
    """
    retained = []
    lost = []
    partial = []

    for point in original_points:
        retention = check_point_retention(point, new_script)

        if retention["status"] == "retained":
            retained.append(point)
        elif retention["status"] == "partial":
            partial.append(point)
        else:
            lost.append(point)

    retention_rate = len(retained) / len(original_points) if original_points else 0
    retention_with_partial = (len(retained) + len(partial)) / len(original_points) if original_points else 0

    is_acceptable = retention_with_partial >= min_retention

    return {
        "retention_rate": round(retention_rate, 3),
        "retention_with_partial": round(retention_with_partial, 3),
        "min_retention": min_retention,
        "is_acceptable": is_acceptable,
        "retained_points": retained,
        "partial_points": partial,
        "lost_points": lost,
        "summary": {
            "total": len(original_points),
            "retained": len(retained),
            "partial": len(partial),
            "lost": len(lost),
        }
    }


def check_point_retention(point: str, script: str) -> Dict:
    """
    Check if a single point is retained in the script.

    Args:
        point: Original key point
        script: Generated script

    Returns:
        Retention status for the point
    """
    # Extract key concepts from point
    key_concepts = extract_key_concepts(point)

    if not key_concepts:
        return {"status": "no_concepts", "concepts": []}

    # Check how many concepts appear in script
    script_lower = script.lower()
    found_concepts = [c for c in key_concepts if c in script_lower]

    retention_ratio = len(found_concepts) / len(key_concepts)

    if retention_ratio >= 0.8:
        status = "retained"
    elif retention_ratio >= 0.4:
        status = "partial"
    else:
        status = "lost"

    return {
        "status": status,
        "concepts": key_concepts,
        "found": found_concepts,
        "retention_ratio": round(retention_ratio, 3),
    }


def extract_key_concepts(text: str) -> List[str]:
    """
    Extract key concepts from text.

    Args:
        text: Input text

    Returns:
        List of key concepts
    """
    # Remove common words
    stop_words = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "should",
        "could", "might", "must", "can", "this", "that", "these", "those",
        "的", "了", "是", "在", "有", "和", "与", "或", "但是", "然后", "因为",
    }

    # Extract nouns and meaningful words
    words = re.findall(r'\b\w{3,}\b', text.lower())

    # Filter stop words
    key_words = [w for w in words if w not in stop_words]

    # Return unique words
    return list(set(key_words))


# ============================================================================
# QUALITY SCORING SYSTEM
# ============================================================================

def calculate_quality_scores(package: dict, original_transcript: str) -> Dict:
    """
    Calculate comprehensive quality scores for a Level 2 package.

    Args:
        package: Level 2 script package
        original_transcript: Original transcript text

    Returns:
        Quality scores dictionary
    """
    scores = {
        "coherence": score_coherence(package),
        "actionability": score_actionability(package),
        "originality": score_originality(package, original_transcript),
        "value_retention": score_value_retention(package, original_transcript),
    }

    # Calculate overall score
    overall = sum(scores.values()) / len(scores)

    return {
        "scores": scores,
        "overall": round(overall, 2),
        "is_production_ready": overall >= 8.0,
        "is_acceptable": overall >= 6.0,
        "grade": calculate_grade(overall),
    }


def score_coherence(package: dict) -> float:
    """
    Score script coherence.

    Checks:
    - Section flow and transitions
    - Logical progression
    - Clear structure

    Args:
        package: Level 2 package

    Returns:
        Coherence score (0-10)
    """
    script_sections = package.get("script_sections", [])
    if not script_sections:
        return 0.0

    score = 5.0  # Base score

    # Check for clear sections
    has_hook = any("hook" in s.get("section", "").lower() for s in script_sections)
    has_close = any("close" in s.get("section", "").lower() for s in script_sections)

    if has_hook:
        score += 1.5
    if has_close:
        score += 1.5

    # Check section count (good balance: 4-7 sections)
    section_count = len(script_sections)
    if 4 <= section_count <= 7:
        score += 1.0
    elif 3 <= section_count <= 8:
        score += 0.5

    # Check for narrative in each section
    sections_with_narration = sum(
        1 for s in script_sections
        if s.get("narration") and len(s["narration"]) > 20
    )

    narration_ratio = sections_with_narration / len(script_sections)
    score += narration_ratio * 1.0

    return min(score, 10.0)


def score_actionability(package: dict) -> float:
    """
    Score actionability (how easy to produce).

    Checks:
    - Visual direction specificity
    - Shot plan details
    - Clear asset requirements

    Args:
        package: Level 2 package

    Returns:
        Actionability score (0-10)
    """
    script_sections = package.get("script_sections", [])
    shot_plan = package.get("shot_plan", [])

    if not script_sections:
        return 0.0

    score = 5.0  # Base score

    # Check visual direction specificity
    sections_with_detailed_visual = sum(
        1 for s in script_sections
        if s.get("visual_direction") and len(s["visual_direction"]) > 50
    )

    visual_ratio = sections_with_detailed_visual / len(script_sections)
    score += visual_ratio * 2.0

    # Check shot plan
    if shot_plan:
        # Look for detailed specifications
        detailed_shots = sum(
            1 for shot in shot_plan
            if any(k in shot for k in ["shot_type", "camera_angle", "camera_movement"])
        )

        if len(shot_plan) > 0:
            shot_detail_ratio = detailed_shots / len(shot_plan)
            score += shot_detail_ratio * 2.0

    # Check for on-screen text
    sections_with_ost = sum(
        1 for s in script_sections
        if s.get("on_screen_text")
    )

    if len(script_sections) > 0:
        ost_ratio = sections_with_ost / len(script_sections)
        score += ost_ratio * 1.0

    return min(score, 10.0)


def score_originality(package: dict, original_transcript: str) -> float:
    """
    Score originality (how different from source).

    Checks:
    - Semantic similarity
    - Direct phrase copying
    - Fresh angles

    Args:
        package: Level 2 package
        original_transcript: Original transcript text

    Returns:
        Originality score (0-10)
    """
    script_sections = package.get("script_sections", [])

    if not script_sections:
        return 0.0

    score = 5.0  # Base score

    # Check each section for similarity
    similarity_scores = []
    for section in script_sections:
        narration = section.get("narration", "")
        if narration:
            sim_check = check_semantic_similarity(original_transcript, narration)
            similarity_scores.append(sim_check["similarity_score"])

    if similarity_scores:
        avg_similarity = sum(similarity_scores) / len(similarity_scores)

        # Lower similarity = higher originality
        if avg_similarity < 0.3:
            score += 3.0
        elif avg_similarity < 0.5:
            score += 2.0
        elif avg_similarity < 0.7:
            score += 1.0
        else:
            score -= 1.0

    # Check for variety in narration
    narrations = [s.get("narration", "") for s in script_sections]
    unique_narrations = len(set(narrations))

    if unique_narrations == len(narrations):
        score += 1.5  # All unique
    elif unique_narrations >= len(narrations) * 0.8:
        score += 1.0

    return max(0.0, min(score, 10.0))


def score_value_retention(package: dict, original_transcript: str) -> float:
    """
    Score value retention (core message preserved).

    Checks:
    - Key points retained
    - Main concepts present
    - Educational value kept

    Args:
        package: Level 2 package
        original_transcript: Original transcript text

    Returns:
        Value retention score (0-10)
    """
    script_sections = package.get("script_sections", [])

    if not script_sections:
        return 0.0

    # Extract key points from original
    original_points = extract_key_concepts(original_transcript)[:10]

    if not original_points:
        return 5.0  # Can't assess, give neutral score

    # Combine all narrations
    all_narrations = " ".join(s.get("narration", "") for s in script_sections)

    # Check retention
    retention_check = check_key_point_retention(original_points, all_narrations)

    # Score based on retention rate
    retention_rate = retention_check["retention_with_partial"]

    score = retention_rate * 10.0

    # Bonus for having retained points
    if retention_check["summary"]["retained"] >= 3:
        score += 1.0

    # Penalty for losing many points
    if retention_check["summary"]["lost"] > len(original_points) * 0.3:
        score -= 2.0

    return max(0.0, min(score, 10.0))


def calculate_grade(score: float) -> str:
    """
    Calculate letter grade from numeric score.

    Args:
        score: Numeric score (0-10)

    Returns:
        Letter grade
    """
    if score >= 9.0:
        return "A"
    elif score >= 8.0:
        return "B+"
    elif score >= 7.0:
        return "B"
    elif score >= 6.0:
        return "C"
    else:
        return "F"


# ============================================================================
# COPYRIGHT RISK ASSESSMENT
# ============================================================================

def assess_copyright_risk(package: dict, original_transcript: str) -> Dict:
    """
    Assess copyright risk of generated script.

    Args:
        package: Level 2 package
        original_transcript: Original transcript text

    Returns:
        Copyright risk assessment
    """
    script_sections = package.get("script_sections", [])

    risk_factors = []
    total_risk = 0.0

    # Check 1: Direct quotation
    direct_quotes = find_direct_quotations(script_sections, original_transcript)
    if direct_quotes:
        risk_factors.append({
            "type": "direct_quotation",
            "severity": "high",
            "count": len(direct_quotes),
            "examples": direct_quotes[:3],
        })
        total_risk += 0.4 * len(direct_quotes)

    # Check 2: Phrase copying
    phrase_copying = find_phrase_copying(script_sections, original_transcript)
    if phrase_copying:
        risk_factors.append({
            "type": "phrase_copying",
            "severity": "medium",
            "count": len(phrase_copying),
            "examples": phrase_copying[:3],
        })
        total_risk += 0.2 * len(phrase_copying)

    # Check 3: High similarity
    similarity_issues = find_high_similarity_sections(script_sections, original_transcript)
    if similarity_issues:
        risk_factors.append({
            "type": "high_similarity",
            "severity": "medium",
            "count": len(similarity_issues),
            "sections": [s["section"] for s in similarity_issues],
        })
        total_risk += 0.15 * len(similarity_issues)

    # Determine overall risk
    if total_risk >= 1.0:
        risk_level = "high"
        recommendation = "major_revision"
    elif total_risk >= 0.5:
        risk_level = "medium"
        recommendation = "revision"
    elif total_risk >= 0.2:
        risk_level = "low"
        recommendation = "review"
    else:
        risk_level = "minimal"
        recommendation = "approve"

    return {
        "risk_level": risk_level,
        "total_risk_score": round(total_risk, 3),
        "recommendation": recommendation,
        "risk_factors": risk_factors,
        "safe_for_commercial_use": risk_level == "minimal",
    }


def find_direct_quotations(script_sections: List[dict], original: str) -> List[str]:
    """Find direct quotations from original in script."""
    quotations = []

    original_sentences = re.split(r'[.!?。！？]', original)
    original_sentences = [s.strip() for s in original_sentences if len(s.strip()) > 10]

    for section in script_sections:
        narration = section.get("narration", "")

        for orig_sent in original_sentences:
            if orig_sent.lower() in narration.lower():
                quotations.append(orig_sent[:50] + "..." if len(orig_sent) > 50 else orig_sent)

    return quotations


def find_phrase_copying(script_sections: List[dict], original: str) -> List[str]:
    """Find copied phrases from original in script."""
    copied = []

    original_phrases = extract_phrases(original, min_length=4)

    for section in script_sections:
        narration = section.get("narration", "")

        for phrase in original_phrases:
            if phrase.lower() in narration.lower():
                copied.append(phrase)

    return copied[:10]  # Limit to top 10


def find_high_similarity_sections(
    script_sections: List[dict],
    original: str
) -> List[dict]:
    """Find sections with high similarity to original."""
    high_sim = []

    for section in script_sections:
        narration = section.get("narration", "")

        if len(narration) > 20:
            sim_check = check_semantic_similarity(original, narration, threshold=0.6)

            if sim_check["is_too_similar"]:
                high_sim.append({
                    "section": section.get("section", "unknown"),
                    "similarity": sim_check["similarity_score"],
                })

    return high_sim


# ============================================================================
# COMPREHENSIVE VALIDATION REPORT
# ============================================================================

def generate_validation_report(
    package: dict,
    original_transcript: str,
    transcript_path: Path
) -> Dict:
    """
    Generate comprehensive validation report for a Level 2 package.

    Args:
        package: Level 2 script package
        original_transcript: Original transcript text
        transcript_path: Path to transcript file

    Returns:
        Complete validation report
    """
    # Calculate quality scores
    quality_scores = calculate_quality_scores(package, original_transcript)

    # Assess copyright risk
    copyright_assessment = assess_copyright_risk(package, original_transcript)

    # Check key point retention
    original_points = extract_key_concepts(original_transcript)[:10]
    all_narrations = " ".join(
        s.get("narration", "") for s in package.get("script_sections", [])
    )
    retention_check = check_key_point_retention(original_points, all_narrations)

    # Section-by-section similarity check
    section_similarities = []
    for section in package.get("script_sections", []):
        if section.get("narration"):
            sim_check = check_section_similarity(
                original_transcript[:500],  # Use first part for comparison
                section["narration"]
            )
            section_similarities.append({
                "section": section.get("section"),
                "similarity": sim_check["similarity_score"],
                "recommendation": sim_check["recommendation"],
            })

    # Compile report
    report = {
        "timestamp": datetime.now().isoformat(),
        "transcript_path": str(transcript_path),
        "package_version": package.get("version", "1.0"),
        "content_type": package.get("source", {}).get("content_type", "unknown"),
        "quality_scores": quality_scores,
        "copyright_assessment": copyright_assessment,
        "key_point_retention": retention_check,
        "section_similarities": section_similarities,
        "overall_assessment": {
            "status": determine_overall_status(quality_scores, copyright_assessment),
            "recommendation": determine_recommendation(quality_scores, copyright_assessment),
            "confidence": calculate_confidence(quality_scores, copyright_assessment),
        }
    }

    return report


def determine_overall_status(quality_scores: dict, copyright_assessment: dict) -> str:
    """Determine overall status from scores and assessment."""
    if copyright_assessment["risk_level"] == "high":
        return "needs_revision"

    overall_score = quality_scores["overall"]

    if overall_score >= 8.0:
        return "production_ready"
    elif overall_score >= 6.0:
        return "acceptable"
    else:
        return "needs_improvement"


def determine_recommendation(quality_scores: dict, copyright_assessment: dict) -> str:
    """Determine action recommendation."""
    status = determine_overall_status(quality_scores, copyright_assessment)

    recommendations = {
        "production_ready": "Approved for production use. Minor polish optional.",
        "acceptable": "Acceptable for use. Consider improvements for better quality.",
        "needs_improvement": "Requires revision before use. Focus on lowest-scoring areas.",
        "needs_revision": "Must revise due to copyright concerns or poor quality.",
    }

    return recommendations.get(status, "Review needed.")


def calculate_confidence(quality_scores: dict, copyright_assessment: dict) -> str:
    """Calculate confidence in assessment."""
    overall_score = quality_scores["overall"]
    risk_level = copyright_assessment["risk_level"]

    if risk_level == "minimal" and overall_score >= 8.0:
        return "high"
    elif risk_level == "low" and overall_score >= 7.0:
        return "medium"
    else:
        return "low"


def render_validation_report_markdown(report: dict) -> str:
    """Render validation report as markdown."""
    lines = [
        "# Level 2 Validation Report",
        "",
        f"**Generated:** {report['timestamp']}",
        f"**Content Type:** {report['content_type']}",
        "",
        "---",
        "",
        "## 📊 Overall Assessment",
        "",
        f"**Status:** {report['overall_assessment']['status'].upper()}",
        f"**Recommendation:** {report['overall_assessment']['recommendation']}",
        f"**Confidence:** {report['overall_assessment']['confidence'].title()}",
        "",
    ]

    # Quality scores
    scores = report["quality_scores"]
    lines.extend([
        "## 🎯 Quality Scores",
        "",
        f"| Dimension | Score |",
        f"|-----------|-------|",
        f"| Coherence | {scores['scores']['coherence']}/10 |",
        f"| Actionability | {scores['scores']['actionability']}/10 |",
        f"| Originality | {scores['scores']['originality']}/10 |",
        f"| Value Retention | {scores['scores']['value_retention']}/10 |",
        f"| **Overall** | **{scores['overall']}/10** |",
        f"| **Grade** | **{scores['grade']}** |",
        "",
    ])

    # Copyright assessment
    copyright = report["copyright_assessment"]
    lines.extend([
        "## ⚖️ Copyright Risk Assessment",
        "",
        f"**Risk Level:** {copyright['risk_level'].upper()}",
        f"**Risk Score:** {copyright['total_risk_score']}",
        f"**Safe for Commercial Use:** {'✅ Yes' if copyright['safe_for_commercial_use'] else '❌ No'}",
        "",
    ])

    if copyright["risk_factors"]:
        lines.extend([
            "**Risk Factors:**",
            ""
        ])
        for factor in copyright["risk_factors"]:
            lines.append(f"- **{factor['type'].title()}** ({factor['severity']}): {factor.get('count', 'N/A')} instances")

    # Key point retention
    retention = report["key_point_retention"]
    lines.extend([
        "",
        "## 🔑 Key Point Retention",
        "",
        f"**Retention Rate:** {retention['retention_rate']:.1%}",
        f"**With Partial:** {retention['retention_with_partial']:.1%}",
        f"**Status:** {'✅ Acceptable' if retention['is_acceptable'] else '❌ Needs Improvement'}",
        "",
        f"- Retained: {retention['summary']['retained']}",
        f"- Partial: {retention['summary']['partial']}",
        f"- Lost: {retention['summary']['lost']}",
        "",
    ])

    # Recommendations
    lines.extend([
        "---",
        "",
        "## 💡 Recommendations",
        "",
    ])

    status = report["overall_assessment"]["status"]

    if status == "production_ready":
        lines.extend([
            "✅ This package is ready for production use.",
            "",
            "Optional improvements:",
            "- Minor polish for highest quality",
            "- Test with target audience",
        ])
    elif status == "acceptable":
        lines.extend([
            "🟡 This package is acceptable but could be improved.",
            "",
            "Suggested improvements:",
            "- Focus on lowest-scoring dimensions",
            "- Review and refine weak sections",
            "- Consider additional visual direction details",
        ])
    else:
        lines.extend([
            "🔴 This package needs revision before use.",
            "",
            "Required actions:",
            "- Address copyright concerns if present",
            "- Improve lowest-scoring areas",
            "- Ensure key points are retained",
            "- Revise similar sections",
        ])

    lines.extend([
        "",
        "---",
        "",
        "*Generated by Level 2 Validation Module*",
    ])

    return "\n".join(lines)


def save_validation_report(
    package_dir: Path,
    report: dict
) -> Path:
    """
    Save validation report to package directory.

    Args:
        package_dir: Package directory path
        report: Validation report dictionary

    Returns:
        Path to saved report
    """
    # Save JSON
    report_json = package_dir / "validation_report.json"
    with open(report_json, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # Save Markdown
    report_md = package_dir / "validation_report.md"
    report_md.write_text(render_validation_report_markdown(report), encoding="utf-8")

    return report_md
