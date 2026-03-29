"""
Processing Service

Connects API endpoints to actual OpenFang processing logic.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
import logging
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.level2_improved import (
    build_improved_level2_package,
    detect_content_type,
    ContentType
)
from scripts.level2_validation import calculate_quality_scores, assess_copyright_risk
from auto_clip import build_transcript_payload, OUTPUT_DIR

logger = logging.getLogger(__name__)


class ProcessingService:
    """Service for processing video/transcript requests"""

    def __init__(self):
        """Initialize processing service"""
        self.output_dir = OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def process_transcript(
        self,
        transcript_path: str,
        level: int,
        config: Dict[str, Any],
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Process a transcript file.

        Args:
            transcript_path: Path to transcript file
            level: Transformation level (1, 2, or 3)
            config: Processing configuration
            progress_callback: Optional callback for progress updates

        Returns:
            Processing result with output path

        Raises:
            ValueError: If parameters are invalid
            ProcessingError: If processing fails
        """
        try:
            # Validate level
            if level not in [1, 2, 3]:
                raise ValueError(f"Invalid level: {level}")

            # Validate transcript exists
            transcript_file = Path(transcript_path)
            if not transcript_file.exists():
                raise ValueError(f"Transcript not found: {transcript_path}")

            logger.info(f"Processing transcript: {transcript_file.name}, Level: {level}")

            # Progress: 10%
            if progress_callback:
                await progress_callback(10, "Loading transcript...")

            # Load transcript
            transcript = build_transcript_payload(transcript_file)
            if not transcript:
                raise ValueError("Failed to load transcript")

            # Progress: 30%
            if progress_callback:
                await progress_callback(30, "Analyzing content...")

            # Build video info
            video_info = {
                "title": transcript_file.stem,
                "path": str(transcript_file),
                "config": config
            }

            # Process based on level
            if level == 2:
                # Progress: 50%
                if progress_callback:
                    await progress_callback(50, "Generating Level 2 package...")

                # Detect content type if not specified
                content_type = config.get("content_type", "auto")
                if content_type == "auto":
                    detected = detect_content_type(transcript, video_info)
                    content_type = detected.value
                    logger.info(f"Auto-detected content type: {content_type}")

                # Generate Level 2 package
                config["content_type"] = content_type
                package = build_improved_level2_package(
                    video_info,
                    transcript,
                    transcript_file,
                    config
                )

                if not package:
                    raise ValueError("Failed to generate Level 2 package")

                # Progress: 80%
                if progress_callback:
                    await progress_callback(80, "Saving package...")

                # Save package
                output_file = self.output_dir / f"{transcript_file.stem}_level2.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(package, f, ensure_ascii=False, indent=2)

                # Progress: 100%
                if progress_callback:
                    await progress_callback(100, "Complete!")

                return {
                    "level": level,
                    "output_path": str(output_file),
                    "content_type": content_type,
                    "package": package
                }

            elif level == 1:
                # Level 1: Visual remix (placeholder)
                if progress_callback:
                    await progress_callback(50, "Applying visual remix...")

                # TODO: Implement Level 1 processing
                result = {
                    "level": level,
                    "output_path": str(transcript_file),
                    "message": "Level 1 processing not yet implemented"
                }

                if progress_callback:
                    await progress_callback(100, "Complete!")

                return result

            elif level == 3:
                # Level 3: Complete recreation (placeholder)
                if progress_callback:
                    await progress_callback(50, "Creating complete recreation...")

                # TODO: Implement Level 3 processing
                result = {
                    "level": level,
                    "output_path": str(transcript_file),
                    "message": "Level 3 processing not yet implemented"
                }

                if progress_callback:
                    await progress_callback(100, "Complete!")

                return result

        except Exception as e:
            logger.error(f"Processing failed: {e}", exc_info=True)
            raise

    def validate_package(
        self,
        package_path: str,
        original_transcript: str = ""
    ) -> Dict[str, Any]:
        """
        Validate a Level 2 package.

        Args:
            package_path: Path to package JSON
            original_transcript: Original transcript for copyright check

        Returns:
            Validation results
        """
        try:
            # Load package
            package_file = Path(package_path)
            if not package_file.exists():
                raise ValueError(f"Package not found: {package_path}")

            with open(package_file, 'r', encoding='utf-8') as f:
                package = json.load(f)

            # Calculate quality scores
            quality_result = calculate_quality_scores(package, original_transcript)

            # Assess copyright risk
            copyright_result = assess_copyright_risk(package, original_transcript)

            # Combine results
            return {
                **quality_result,
                "copyright_risk": copyright_result
            }

        except Exception as e:
            logger.error(f"Validation failed: {e}", exc_info=True)
            raise


# Singleton instance
_processing_service = None


def get_processing_service() -> ProcessingService:
    """Get the processing service instance"""
    global _processing_service
    if _processing_service is None:
        _processing_service = ProcessingService()
    return _processing_service
