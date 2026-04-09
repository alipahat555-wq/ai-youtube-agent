"""
UPLOADER - Prepares video metadata for YouTube
Saves metadata JSON for reference
"""

import logging
import json
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime

from config import Config


class VideoUploader:
    """Prepare videos and metadata for upload."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.config = Config()
    
    def save_metadata(
        self,
        script_data: Dict,
        video_path: Path
    ) -> Optional[Path]:
        """
        Save video metadata to JSON file.
        
        Args:
            script_data: Script dictionary
            video_path: Path to video file
            
        Returns:
            Path to metadata JSON file
        """
        try:
            self.logger.info("Saving metadata...")
            
            # Validate inputs
            if not video_path.exists():
                self.logger.error(f"Video file not found: {video_path}")
                return None
            
            if not script_data:
                self.logger.error("Script data is empty")
                return None
            
            # Create metadata
            metadata = {
                "title": script_data.get("title", "Video"),
                "description": script_data.get("description", ""),
                "tags": script_data.get("tags", []),
                "niche": script_data.get("niche", ""),
                "topic": script_data.get("topic", ""),
                "video_path": str(video_path),
                "video_size": video_path.stat().st_size,
                "created_at": datetime.now().isoformat(),
                "privacy_status": "private",
                "made_for_kids": False,
                "category_id": "24"  # Entertainment
            }
            
            # Save to JSON
            output_dir = Path(self.config.OUTPUT_DIR)
            metadata_path = output_dir / f"{video_path.stem}_metadata.json"
            
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            if not metadata_path.exists():
                self.logger.error(f"Metadata file not created: {metadata_path}")
                return None
            
            self.logger.info(f"✓ Metadata saved ({metadata_path.name})")
            return metadata_path
            
        except Exception as e:
            self.logger.error(f"Metadata save error: {e}", exc_info=True)
            return None
