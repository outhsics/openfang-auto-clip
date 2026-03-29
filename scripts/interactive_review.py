#!/usr/bin/env python3
"""
Interactive Level 2 Package Review Tool

This script provides an interactive CLI for reviewing and editing
Level 2 script packages with real-time validation feedback.

Features:
- Interactive section-by-section review
- Edit narration and visual direction
- Real-time quality scoring
- Multiple export formats (PDF, DOCX, Markdown, JSON)

Usage:
    python scripts/interactive_review.py --package <path>
    python scripts/interactive_review.py --latest
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.level2_validation import (
    calculate_quality_scores,
    check_section_similarity,
)


class InteractiveReviewer:
    """Interactive CLI for reviewing Level 2 packages."""

    def __init__(self, package_path: Path):
        """Initialize reviewer with package path."""
        self.package_path = self._resolve_package_path(package_path)
        self.package = self._load_package()
        self.original_transcript = self._load_original_transcript()
        self.modified = False

    def _resolve_package_path(self, path: Path) -> Path:
        """Resolve package path (directory or JSON file)."""
        if path.is_dir():
            json_path = path / "script_package.json"
            if json_path.exists():
                return json_path
        elif path.is_file() and path.suffix == ".json":
            return path
        else:
            # Try to find in default location
            from auto_clip import OUTPUT_DIR
            latest = list((OUTPUT_DIR / "script_packages").glob("*/script_package.json"))
            if latest:
                return max(latest, key=lambda p: p.stat().st_mtime)
            raise FileNotFoundError(f"Package not found: {path}")

    def _load_package(self) -> dict:
        """Load package from JSON file."""
        with open(self.package_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_original_transcript(self) -> str:
        """Load original transcript for comparison."""
        transcript_path = self.package.get("source", {}).get("transcript_path")
        if transcript_path and Path(transcript_path).exists():
            with open(transcript_path, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def review(self):
        """Start interactive review session."""
        self._print_header()

        while True:
            self._print_menu()
            choice = input("\nChoose an action: ").strip().lower()

            if choice in ["1", "overview"]:
                self._show_overview()
            elif choice in ["2", "sections"]:
                self._review_sections()
            elif choice in ["3", "quality"]:
                self._show_quality_scores()
            elif choice in ["4", "edit"]:
                self._edit_section()
            elif choice in ["5", "validate"]:
                self._run_validation()
            elif choice in ["6", "export"]:
                self._export_package()
            elif choice in ["7", "compare"]:
                self._compare_with_original()
            elif choice in ["8", "save"]:
                self._save_changes()
            elif choice in ["9", "help"]:
                self._show_help()
            elif choice in ["0", "q", "quit", "exit"]:
                if self.modified:
                    confirm = input("You have unsaved changes. Save before exit? (y/n): ").strip().lower()
                    if confirm == "y":
                        self._save_changes()
                print("\n✅ Review session ended. Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please try again.")

    def _print_header(self):
        """Print session header."""
        print("=" * 70)
        print("📝 Level 2 Package Interactive Review")
        print("📝 Level 2 脚本包交互式审查")
        print("=" * 70)
        print(f"\n📦 Package: {self.package_path.parent.name}")
        print(f"📄 File: {self.package_path.name}")
        print(f"📝 Content Type: {self.package.get('source', {}).get('content_type', 'N/A')}")
        print(f"🌐 Language: {self.package.get('source', {}).get('language', 'N/A')}")

    def _print_menu(self):
        """Print main menu."""
        print("\n" + "=" * 70)
        print("📋 MAIN MENU")
        print("=" * 70)
        print("1. Overview - Show package overview")
        print("2. Sections - Review all sections")
        print("3. Quality - Show quality scores")
        print("4. Edit - Edit a section")
        print("5. Validate - Run validation check")
        print("6. Export - Export to different format")
        print("7. Compare - Compare with original")
        print("8. Save - Save changes")
        print("9. Help - Show detailed help")
        print("0. Quit - Exit review session")

    def _show_overview(self):
        """Show package overview."""
        print("\n" + "=" * 70)
        print("📊 PACKAGE OVERVIEW")
        print("=" * 70)

        sections = self.package.get("script_sections", [])
        shot_plan = self.package.get("shot_plan", [])

        print(f"\n📈 Statistics:")
        print(f"   • Sections: {len(sections)}")
        print(f"   • Shot plan entries: {len(shot_plan)}")
        print(f"   • Total duration: {sum(s.get('duration', 0) for s in sections)}s")

        print(f"\n📝 Sections:")
        for i, section in enumerate(sections, 1):
            duration = section.get("duration", "N/A")
            print(f"   {i}. {section.get('section', 'Unknown')} ({duration}s)")

        if self.modified:
            print(f"\n⚠️  This package has unsaved changes.")

    def _review_sections(self):
        """Review all sections interactively."""
        sections = self.package.get("script_sections", [])

        if not sections:
            print("\n❌ No sections found in package.")
            return

        for i, section in enumerate(sections):
            self._review_section(i, section)
            print("\n" + "-" * 70)

            if i < len(sections) - 1:
                action = input("Press Enter to continue, 's' to skip to next, 'q' to return: ").strip().lower()
                if action == "q":
                    break
                elif action == "s":
                    continue

    def _review_section(self, index: int, section: dict):
        """Review a single section."""
        print("\n" + "=" * 70)
        print(f"📝 SECTION {index + 1}: {section.get('section', 'Unknown')}")
        print("=" * 70)

        print(f"\n⏱️  Duration: {section.get('duration', 'N/A')}s")

        print(f"\n🎭 Narration:")
        print(f"   {section.get('narration', 'N/A')}")

        print(f"\n📺 On-Screen Text:")
        print(f"   {section.get('on_screen_text', 'N/A')}")

        print(f"\n🎬 Visual Direction:")
        visual = section.get('visual_direction', 'N/A')
        # Truncate if too long
        if len(visual) > 300:
            visual = visual[:300] + "..."
        print(f"   {visual}")

        if section.get('source_anchor'):
            print(f"\n⚓️  Source Anchor: {section['source_anchor']}")

    def _show_quality_scores(self):
        """Show quality scores for the package."""
        print("\n" + "=" * 70)
        print("🎯 QUALITY SCORES")
        print("=" * 70)

        try:
            scores = calculate_quality_scores(self.package, self.original_transcript)

            print(f"\n📊 Scores:")
            for dimension, score in scores["scores"].items():
                status = "✅" if score >= 8 else "🟡" if score >= 6 else "❌"
                print(f"   {status} {dimension.title()}: {score}/10")

            print(f"\n📈 Overall: {scores['overall']}/10 ({scores['grade']})")
            print(f"📌 Status: {scores['is_production_ready']}")

            if not scores["is_production_ready"]:
                print(f"\n💡 Suggestions for improvement:")
                if scores["scores"]["coherence"] < 8:
                    print("   • Improve section transitions")
                if scores["scores"]["actionability"] < 8:
                    print("   • Add more specific visual direction")
                if scores["scores"]["originality"] < 8:
                    print("   • Rewrite to be more different from original")
                if scores["scores"]["value_retention"] < 8:
                    print("   • Ensure key points are preserved")

        except Exception as e:
            print(f"\n❌ Error calculating scores: {e}")

    def _edit_section(self):
        """Edit a section."""
        sections = self.package.get("script_sections", [])

        if not sections:
            print("\n❌ No sections to edit.")
            return

        print("\n" + "=" * 70)
        print("✏️  EDIT SECTION")
        print("=" * 70)

        # Select section
        print("\nSelect section to edit:")
        for i, section in enumerate(sections):
            print(f"   {i + 1}. {section.get('section', 'Unknown')}")

        try:
            choice = int(input("\nEnter section number: ").strip())
            if choice < 1 or choice > len(sections):
                print("❌ Invalid section number.")
                return
        except ValueError:
            print("❌ Please enter a valid number.")
            return

        section = sections[choice - 1]

        # Edit fields
        print(f"\nEditing: {section.get('section', 'Unknown')}")
        print("Leave blank to keep current value.\n")

        # Edit narration
        print(f"Current narration: {section.get('narration', '')[:100]}...")
        new_narration = input("New narration: ").strip()
        if new_narration:
            section["narration"] = new_narration
            print("✅ Narration updated")

        # Edit on-screen text
        print(f"\nCurrent on-screen text: {section.get('on_screen_text', '')}")
        new_ost = input("New on-screen text: ").strip()
        if new_ost:
            section["on_screen_text"] = new_ost
            print("✅ On-screen text updated")

        # Edit visual direction
        current_visual = section.get('visual_direction', '')
        print(f"\nCurrent visual direction: {current_visual[:100]}...")
        new_visual = input("New visual direction (multi-line, end with empty line): ").strip()

        if new_visual:
            # Read multi-line input
            lines = [new_visual]
            while True:
                line = input().strip()
                if not line:
                    break
                lines.append(line)
            section["visual_direction"] = "\n".join(lines)
            print("✅ Visual direction updated")

        # Check similarity if original transcript available
        if self.original_transcript and section.get("narration"):
            print("\n🔍 Checking similarity with original...")
            sim_check = check_section_similarity(
                self.original_transcript[:500],
                section["narration"]
            )
            print(f"   Similarity: {sim_check['similarity_score']:.2%}")
            print(f"   Recommendation: {sim_check['recommendation']}")

        self.modified = True
        print("\n✅ Section updated successfully!")

    def _run_validation(self):
        """Run validation on the package."""
        print("\n" + "=" * 70)
        print("🔍 RUNNING VALIDATION")
        print("=" * 70)

        if not self.original_transcript:
            print("\n⚠️  Original transcript not available. Limited validation.")

        try:
            from scripts.level2_validation import (
                assess_copyright_risk,
                check_key_point_retention,
                extract_key_concepts,
            )

            # Copyright risk
            if self.original_transcript:
                print("\n⚖️  Copyright Risk Assessment:")
                copyright = assess_copyright_risk(self.package, self.original_transcript)
                print(f"   Risk Level: {copyright['risk_level'].upper()}")
                print(f"   Risk Score: {copyright['total_risk_score']}")
                print(f"   Safe for Commercial: {'✅ Yes' if copyright['safe_for_commercial_use'] else '❌ No'}")

                if copyright['risk_factors']:
                    print(f"\n   Risk Factors:")
                    for factor in copyright['risk_factors']:
                        print(f"   • {factor['type'].title()}: {factor.get('count', 'N/A')} instances")

            # Key point retention
            if self.original_transcript:
                print(f"\n🔑 Key Point Retention:")
                points = extract_key_concepts(self.original_transcript)[:10]
                all_narrations = " ".join(
                    s.get("narration", "") for s in self.package.get("script_sections", [])
                )
                retention = check_key_point_retention(points, all_narrations)
                print(f"   Retention Rate: {retention['retention_rate']:.1%}")
                print(f"   Status: {'✅ Acceptable' if retention['is_acceptable'] else '❌ Needs Improvement'}")

        except Exception as e:
            print(f"\n❌ Validation error: {e}")
            import traceback
            traceback.print_exc()

    def _export_package(self):
        """Export package to different format."""
        print("\n" + "=" * 70)
        print("📤 EXPORT PACKAGE")
        print("=" * 70)

        print("\nSelect export format:")
        print("   1. Markdown (.md)")
        print("   2. JSON (.json)")
        print("   3. Text (.txt)")

        choice = input("\nEnter choice: ").strip()

        if choice == "1":
            self._export_markdown()
        elif choice == "2":
            self._export_json()
        elif choice == "3":
            self._export_text()
        else:
            print("❌ Invalid choice.")

    def _export_markdown(self):
        """Export package as Markdown."""
        output_path = self.package_path.parent / "script_export.md"

        lines = [
            "# Level 2 Script Package",
            "",
            f"**Exported:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Content Type:** {self.package.get('source', {}).get('content_type', 'N/A')}",
            "",
            "---",
            "",
            "## Script Sections",
            "",
        ]

        for section in self.package.get("script_sections", []):
            lines.extend([
                f"### {section.get('section')} ({section.get('duration')}s)",
                "",
                f"**Narration:** {section.get('narration', '')}",
                "",
                f"**On-Screen Text:** {section.get('on_screen_text', '')}",
                "",
                f"**Visual Direction:** {section.get('visual_direction', '')}",
                "",
                "---",
                "",
            ])

        output_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"\n✅ Exported to: {output_path}")

    def _export_json(self):
        """Export package as JSON (pretty-printed)."""
        output_path = self.package_path.parent / "script_export.json"

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.package, f, ensure_ascii=False, indent=2)

        print(f"\n✅ Exported to: {output_path}")

    def _export_text(self):
        """Export package as plain text."""
        output_path = self.package_path.parent / "script_export.txt"

        lines = [
            "LEVEL 2 SCRIPT PACKAGE",
            "=" * 70,
            "",
            f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Content Type: {self.package.get('source', {}).get('content_type', 'N/A')}",
            "",
            "=" * 70,
            "",
        ]

        for section in self.package.get("script_sections", []):
            lines.extend([
                f"SECTION: {section.get('section')} ({section.get('duration')}s)",
                "-" * 70,
                "",
                f"NARRATION:",
                section.get('narration', ''),
                "",
                f"ON-SCREEN TEXT: {section.get('on_screen_text', '')}",
                "",
                f"VISUAL DIRECTION:",
                section.get('visual_direction', ''),
                "",
                "",
            ])

        output_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"\n✅ Exported to: {output_path}")

    def _compare_with_original(self):
        """Compare package with original transcript."""
        if not self.original_transcript:
            print("\n❌ Original transcript not available for comparison.")
            return

        print("\n" + "=" * 70)
        print("🔄 COMPARISON WITH ORIGINAL")
        print("=" * 70)

        sections = self.package.get("script_sections", [])

        print(f"\n📝 Original Transcript (first 200 chars):")
        print(f"   {self.original_transcript[:200]}...")

        print(f"\n📝 Generated Script Sections:")
        for i, section in enumerate(sections[:3], 1):  # Show first 3
            print(f"\n   Section {i}: {section.get('section')}")
            print(f"   Narration: {section.get('narration', '')[:100]}...")

            # Check similarity
            if section.get('narration'):
                sim = check_section_similarity(
                    self.original_transcript[:500],
                    section["narration"]
                )
                print(f"   Similarity: {sim['similarity_score']:.2%} ({sim['recommendation']})")

    def _save_changes(self):
        """Save changes to package."""
        if not self.modified:
            print("\nℹ️  No changes to save.")
            return

        print("\n" + "=" * 70)
        print("💾 SAVING CHANGES")
        print("=" * 70)

        # Create backup
        backup_path = self.package_path.parent / "script_package.backup.json"
        with open(backup_path, "w", encoding="utf-8") as f:
            json.load(open(self.package_path, "r"))  # Load original
            # Backup is already created by file write above
        import shutil
        shutil.copy2(self.package_path, backup_path)
        print(f"   ✅ Backup created: {backup_path.name}")

        # Save changes
        with open(self.package_path, "w", encoding="utf-8") as f:
            json.dump(self.package, f, ensure_ascii=False, indent=2)

        print(f"   ✅ Changes saved to: {self.package_path.name}")
        self.modified = False

    def _show_help(self):
        """Show detailed help."""
        print("\n" + "=" * 70)
        print("❓ HELP")
        print("=" * 70)

        help_text = """
📋 OVERVIEW
    This tool allows you to review and edit Level 2 script packages
    interactively with real-time validation feedback.

🔍 NAVIGATION
    • Use the menu numbers or keywords to navigate
    • Press Enter to continue through sections
    • Type 'q' to return to main menu

✏️  EDITING
    • You can edit narration, on-screen text, and visual direction
    • Leave blank to keep current value
    • Multi-line input for visual direction (end with empty line)

🔍 VALIDATION
    • Checks similarity with original transcript
    • Assesses copyright risk
    • Validates key point retention

📤 EXPORT
    • Export to Markdown, JSON, or plain text
    • Exports are saved in the package directory

💾 SAVING
    • Creates automatic backup before saving
    • Backup saved as script_package.backup.json
    • Prompts to save on exit if modified

💡 TIPS
    • Review quality scores before editing
    • Check similarity after editing
    • Export to your preferred format for production
    • Keep backups for version control
        """
        print(help_text)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Interactive Level 2 package review tool"
    )
    parser.add_argument(
        "--package",
        type=str,
        help="Path to package directory or script_package.json",
    )
    parser.add_argument(
        "--latest",
        action="store_true",
        help="Use the most recent package",
    )

    args = parser.parse_args()

    # Determine package path
    if args.latest:
        from auto_clip import OUTPUT_DIR
        packages_dir = OUTPUT_DIR / "script_packages"
        latest = max(packages_dir.glob("*/script_package.json"), key=lambda p: p.stat().st_mtime)
        package_path = latest.parent
    elif args.package:
        package_path = Path(args.package)
    else:
        parser.print_help()
        print("\n❌ Please specify --package or --latest")
        sys.exit(1)

    # Create reviewer and start session
    try:
        reviewer = InteractiveReviewer(package_path)
        reviewer.review()
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
