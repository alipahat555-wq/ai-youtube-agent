"""
VIDEO CREATOR - Creates vertical videos from audio
Uses FFmpeg for fast, reliable video generation
"""

import logging
import subprocess
from pathlib import Path
from typing import Optional
from datetime import datetime

from config import Config


class VideoCreator:
    """Create vertical 1080x1920 videos from audio."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.config = Config()
    
    def create(
        self,
        audio_path: Path,
        title: str,
        duration: int = 6
    ) -> Optional[Path]:
        """
        Create a vertical video.
        
        Args:
            audio_path: Path to MP3 audio file
            title: Video title (for overlay text)
            duration: Video duration in seconds
            
        Returns:
            Path to created MP4 video or None
        """
        try:
            self.logger.info(f"Creating video ({self.config.VIDEO_WIDTH}x{self.config.VIDEO_HEIGHT})...")
            
            # Validate audio
            if not audio_path.exists():
                self.logger.error(f"Audio file not found: {audio_path}")
                return None
            
            # Create output path
            output_dir = Path(self.config.OUTPUT_DIR)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            video_path = output_dir / f"video_{timestamp}.mp4"
            
            # Create video using FFmpeg
            success = self._create_with_ffmpeg(
                audio_path=audio_path,
                video_path=video_path,
                title=title,
                duration=duration
            )
            
            if not success:
                return None
            
            # Validate output
            if not video_path.exists():
                self.logger.error(f"Video file not created: {video_path}")
                return None
            
            file_size = video_path.stat().st_size
            if file_size < 100000:  # Less than 100KB
                self.logger.error(f"Video too small: {file_size} bytes")
                return None
            
            self.logger.info(f"✓ Video created ({file_size / 1024 / 1024:.2f} MB)")
            return video_path
            
        except Exception as e:
            self.logger.error(f"Video creation error: {e}", exc_info=True)
            return None
    
    def _create_with_ffmpeg(
        self,
        audio_path: Path,
        video_path: Path,
        title: str,
        duration: int
    ) -> bool:
        """
        Use FFmpeg to create the video.
        Creates black background with centered text overlay.
        """
        try:
            self.logger.info("Running FFmpeg...")
            
            # Escape special characters in title for FFmpeg
            escaped_title = title.replace("'", "\\'").replace('"', '\\"')
            
            # FFmpeg command
            cmd = [
                "ffmpeg",
                "-f", "lavfi",
                "-i", f"color=c=0x000000:s={self.config.VIDEO_WIDTH}x{self.config.VIDEO_HEIGHT}:d={duration}",
                "-i", str(audio_path),
                "-vf", f"drawtext=text='{escaped_title}':fontsize=50:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2",
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "23",
                "-c:a", "aac",
                "-b:a", "128k",
                "-pix_fmt", "yuv420p",
                "-shortest",
                "-y",
                str(video_path)
            ]
            
            # Run FFmpeg
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config.TIMEOUT_SECONDS
            )
            
            if result.returncode != 0:
                self.logger.error(f"FFmpeg failed: {result.stderr}")
                return False
            
            self.logger.info("✓ FFmpeg completed")
            return True
            
        except subprocess.TimeoutExpired:
            self.logger.error("FFmpeg command timed out")
            return False
        except Exception as e:
            self.logger.error(f"FFmpeg execution error: {e}", exc_info=True)
            return False
