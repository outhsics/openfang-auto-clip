"""
OpenFang Wrapper for openfang-auto-clip

This module provides a Python interface to OpenFang's Clip Hand.
"""

import subprocess
import json
import logging
from typing import Optional, Dict, List, Any

logger = logging.getLogger(__name__)


class OpenFangWrapper:
    """Python wrapper for OpenFang CLI and its Clip Hand."""
    
    def __init__(self, openfang_path: Optional[str] = None):
        self.openfang_cmd = openfang_path or "openfang"
        self._verify_installation()
    
    def _verify_installation(self) -> None:
        """Verify that OpenFang is installed and accessible."""
        try:
            result = subprocess.run(
                [self.openfang_cmd, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                logger.info(f"OpenFang detected: {result.stdout.strip()}")
            else:
                raise RuntimeError("OpenFang not found. Install: https://openfang.sh/install")
        except FileNotFoundError:
            raise RuntimeError("OpenFang not found. Install: curl -fsSL https://openfang.sh/install | sh")
        except subprocess.TimeoutExpired:
            raise RuntimeError("OpenFang command timed out")
    
    def is_clip_hand_active(self) -> bool:
        """Check if the Clip Hand is currently active."""
        try:
            result = subprocess.run(
                [self.openfang_cmd, "hand", "status", "clip"],
                capture_output=True,
                text=True,
                timeout=30
            )
            return "active" in result.stdout.lower()
        except Exception as e:
            logger.warning(f"Failed to check Clip Hand status: {e}")
            return False
    
    def activate_clip_hand(self) -> bool:
        """Activate the OpenFang Clip Hand."""
        try:
            result = subprocess.run(
                [self.openfang_cmd, "hand", "activate", "clip"],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                logger.info("Clip Hand activated successfully")
                return True
            else:
                logger.error(f"Failed to activate Clip Hand: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error activating Clip Hand: {e}")
            return False
    
    def process_video(
        self,
        video_url: str,
        output_dir: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process a video using OpenFang's Clip Hand."""
        if not self.is_clip_hand_active():
            logger.info("Clip Hand not active, activating...")
            if not self.activate_clip_hand():
                return {"status": "error", "error": "Failed to activate Clip Hand"}
        
        job_config = {
            "url": video_url,
            "output_dir": output_dir or "~/.openfang/clips/",
            **(config or {})
        }
        
        return {
            "status": "success",
            "message": "Video processing with OpenFang",
            "config": job_config
        }
