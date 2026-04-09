#!/usr/bin/env python3
"""
MAIN ORCHESTRATOR - YouTube Automation System
Controls entire pipeline, handles failures, manages logging.
"""

import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict

from config import Config
from utils.script_generator import ScriptGenerator
from utils.tts import TextToSpeech
from utils.video import VideoCreator
from utils.uploader import VideoUploader


class Logger:
    """Custom logger setup - simple and effective."""
    
    @staticmethod
    def setup() -> logging.Logger:
        """Initialize logging with file + console output."""
        # Create logs directory
        log_dir = Path(Config.LOG_DIR)
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create log filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"pipeline_{timestamp}.log"
        
        # Configure logging
        logger = logging.getLogger("YouTubeAutomation")
        logger.setLevel(logging.DEBUG)
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger


class Pipeline:
    """Main automation pipeline controller."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.config = Config()
        
        # Initialize all modules
        self.script_gen = ScriptGenerator(logger)
        self.tts = TextToSpeech(logger)
        self.video_creator = VideoCreator(logger)
        self.uploader = VideoUploader(logger)
        
        # Store results from each step
        self.script_data: Optional[Dict] = None
        self.audio_path: Optional[Path] = None
        self.video_path: Optional[Path] = None
    
    def validate_environment(self) -> bool:
        """Validate all prerequisites before starting."""
        self.logger.info("=" * 80)
        self.logger.info("VALIDATING ENVIRONMENT")
        self.logger.info("=" * 80)
        
        try:
            # Check API keys
            api_key = self.config.get_api_key("OPENAI_API_KEY")
            if not api_key:
                self.logger.error("❌ OPENAI_API_KEY not found in environment")
                return False
            
            self.logger.info("✓ OpenAI API key found")
            
            # Create output directories
            output_dir = Path(self.config.OUTPUT_DIR)
            output_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"✓ Output directory ready: {output_dir}")
            
            log_dir = Path(self.config.LOG_DIR)
            log_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"✓ Log directory ready: {log_dir}")
            
            self.logger.info("✓ Environment validation PASSED\n")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Environment validation failed: {e}")
            return False
    
    def step_1_generate_script(self) -> bool:
        """Step 1: Generate unique viral script."""
        self.logger.info("=" * 80)
        self.logger.info("STEP 1/4: GENERATING SCRIPT")
        self.logger.info("=" * 80)
        
        try:
            # Call script generator
            self.script_data = self.script_gen.generate()
            
            if not self.script_data:
                self.logger.error("❌ Script generation returned None")
                return False
            
            # Validate script
            if not self.script_data.get("script") or len(self.script_data["script"]) < 30:
                self.logger.error("❌ Script is empty or too short")
                return False
            
            # Log results
            self.logger.info(f"✓ Script generated successfully")
            self.logger.info(f"  Title: {self.script_data.get('title', 'N/A')}")
            self.logger.info(f"  Length: {len(self.script_data['script'])} characters")
            self.logger.info(f"  Tags: {', '.join(self.script_data.get('tags', [])[:3])}")
            self.logger.info("✓ STEP 1 PASSED\n")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ STEP 1 FAILED: {e}", exc_info=True)
            return False
    
    def step_2_generate_audio(self) -> bool:
        """Step 2: Convert script to speech."""
        self.logger.info("=" * 80)
        self.logger.info("STEP 2/4: GENERATING AUDIO (TTS)")
        self.logger.info("=" * 80)
        
        try:
            if not self.script_data:
                self.logger.error("❌ No script data from Step 1")
                return False
            
            # Generate audio from script
            self.audio_path = self.tts.generate(
                text=self.script_data["script"],
                voice=self.config.VOICE
            )
            
            if not self.audio_path:
                self.logger.error("❌ Audio generation returned None")
                return False
            
            # Validate audio file
            if not self.audio_path.exists():
                self.logger.error(f"❌ Audio file not created: {self.audio_path}")
                return False
            
            file_size = self.audio_path.stat().st_size
            if file_size < 5000:  # Less than 5KB
                self.logger.error(f"❌ Audio file too small: {file_size} bytes")
                return False
            
            # Log results
            self.logger.info(f"✓ Audio generated successfully")
            self.logger.info(f"  File: {self.audio_path.name}")
            self.logger.info(f"  Size: {file_size / 1024:.1f} KB")
            self.logger.info("✓ STEP 2 PASSED\n")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ STEP 2 FAILED: {e}", exc_info=True)
            return False
    
    def step_3_create_video(self) -> bool:
        """Step 3: Create vertical video."""
        self.logger.info("=" * 80)
        self.logger.info("STEP 3/4: CREATING VIDEO")
        self.logger.info("=" * 80)
        
        try:
            if not self.audio_path or not self.audio_path.exists():
                self.logger.error("❌ No audio file from Step 2")
                return False
            
            if not self.script_data:
                self.logger.error("❌ No script data from Step 1")
                return False
            
            # Create video
            self.video_path = self.video_creator.create(
                audio_path=self.audio_path,
                title=self.script_data.get("title", "Video"),
                duration=self.config.VIDEO_DURATION
            )
            
            if not self.video_path:
                self.logger.error("❌ Video creation returned None")
                return False
            
            # Validate video file
            if not self.video_path.exists():
                self.logger.error(f"❌ Video file not created: {self.video_path}")
                return False
            
            file_size = self.video_path.stat().st_size
            if file_size < 100000:  # Less than 100KB
                self.logger.error(f"❌ Video file too small: {file_size} bytes")
                return False
            
            # Log results
            self.logger.info(f"✓ Video created successfully")
            self.logger.info(f"  File: {self.video_path.name}")
            self.logger.info(f"  Size: {file_size / 1024 / 1024:.2f} MB")
            self.logger.info(f"  Resolution: {self.config.VIDEO_WIDTH}x{self.config.VIDEO_HEIGHT}")
            self.logger.info("✓ STEP 3 PASSED\n")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ STEP 3 FAILED: {e}", exc_info=True)
            return False
    
    def step_4_save_metadata(self) -> bool:
        """Step 4: Save metadata and finalize."""
        self.logger.info("=" * 80)
        self.logger.info("STEP 4/4: SAVING METADATA")
        self.logger.info("=" * 80)
        
        try:
            if not self.video_path or not self.video_path.exists():
                self.logger.error("❌ No video from Step 3")
                return False
            
            if not self.script_data:
                self.logger.error("❌ No script data from Step 1")
                return False
            
            # Save metadata
            metadata_path = self.uploader.save_metadata(
                script_data=self.script_data,
                video_path=self.video_path
            )
            
            if not metadata_path:
                self.logger.error("❌ Metadata save failed")
                return False
            
            if not metadata_path.exists():
                self.logger.error(f"❌ Metadata file not created: {metadata_path}")
                return False
            
            # Log results
            self.logger.info(f"✓ Metadata saved successfully")
            self.logger.info(f"  File: {metadata_path.name}")
            self.logger.info("✓ STEP 4 PASSED\n")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ STEP 4 FAILED: {e}", exc_info=True)
            return False
    
    def cleanup(self):
        """Clean up temporary files."""
        try:
            self.logger.info("Cleaning up temporary files...")
            
            # Delete temp audio if configured
            if self.config.CLEANUP_TEMP_AUDIO and self.audio_path:
                if self.audio_path.exists():
                    self.audio_path.unlink()
                    self.logger.info(f"✓ Cleaned: {self.audio_path.name}")
            
            self.logger.info("✓ Cleanup complete")
            
        except Exception as e:
            self.logger.warning(f"Cleanup warning: {e}")
    
    def run(self) -> int:
        """Execute the full pipeline."""
        try:
            # Step 1: Validate
            if not self.validate_environment():
                self.logger.error("\n🔴 PIPELINE STOPPED: Environment validation failed")
                return 1
            
            # Step 2: Generate script
            if not self.step_1_generate_script():
                self.logger.error("\n🔴 PIPELINE STOPPED: Script generation failed")
                return 1
            
            # Step 3: Generate audio
            if not self.step_2_generate_audio():
                self.logger.error("\n🔴 PIPELINE STOPPED: Audio generation failed")
                self.cleanup()
                return 1
            
            # Step 4: Create video
            if not self.step_3_create_video():
                self.logger.error("\n🔴 PIPELINE STOPPED: Video creation failed")
                self.cleanup()
                return 1
            
            # Step 5: Save metadata
            if not self.step_4_save_metadata():
                self.logger.error("\n🔴 PIPELINE STOPPED: Metadata save failed")
                self.cleanup()
                return 1
            
            # Success!
            self.logger.info("=" * 80)
            self.logger.info("🟢 PIPELINE COMPLETED SUCCESSFULLY")
            self.logger.info("=" * 80)
            self.logger.info(f"Video saved to: {self.video_path}")
            self.logger.info("=" * 80 + "\n")
            
            # Cleanup
            self.cleanup()
            
            return 0
            
        except Exception as e:
            self.logger.error(f"\n🔴 FATAL ERROR: {e}", exc_info=True)
            return 1


def main() -> int:
    """Entry point."""
    # Setup logging
    logger = Logger.setup()
    
    # Run pipeline
    pipeline = Pipeline(logger)
    return pipeline.run()


if __name__ == "__main__":
    sys.exit(main())
