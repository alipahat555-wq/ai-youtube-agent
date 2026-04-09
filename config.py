"""
CONFIGURATION - All settings in one place
No hardcoded values, environment-based
"""

import os
from pathlib import Path
from typing import Optional


class Config:
    """Central configuration class."""
    
    # ========== DIRECTORIES ==========
    BASE_DIR = Path(__file__).resolve().parent
    OUTPUT_DIR = BASE_DIR / "output"
    LOG_DIR = BASE_DIR / "logs"
    
    # ========== VIDEO SPECS ==========
    VIDEO_WIDTH = 1080
    VIDEO_HEIGHT = 1920
    VIDEO_DURATION = 6  # seconds (5-8 range)
    VIDEO_FPS = 30
    VIDEO_BITRATE = "3000k"  # Bitrate for quality
    
    # ========== AUDIO SPECS ==========
    AUDIO_FORMAT = "mp3"
    AUDIO_SAMPLE_RATE = 44100
    
    # ========== API SETTINGS ==========
    OPENAI_MODEL = "gpt-4-turbo-preview"
    VOICE = "alloy"  # Options: alloy, echo, fable, onyx, nova, shimmer
    
    # ========== CONTENT SETTINGS ==========
    NICHE = "motivation"  # motivation, asmr, educational
    SCRIPT_LENGTH = 100  # Target words
    LANGUAGE = "en"  # Language for content
    
    # ========== CLEANUP SETTINGS ==========
    CLEANUP_TEMP_AUDIO = False  # Keep audio for debugging
    CLEANUP_TEMP_BACKGROUND = True
    
    # ========== SAFETY SETTINGS ==========
    MAX_RETRIES = 2
    TIMEOUT_SECONDS = 300
    
    @staticmethod
    def get_api_key(key_name: str) -> Optional[str]:
        """
        Safely retrieve API key from environment.
        
        Args:
            key_name: Environment variable name (e.g., 'OPENAI_API_KEY')
            
        Returns:
            API key value or None
        """
        value = os.getenv(key_name)
        
        if not value:
            print(f"⚠️  WARNING: {key_name} not found in environment")
            return None
        
        return value
    
    @staticmethod
    def ensure_directories():
        """Create output and log directories if they don't exist."""
        Path(Config.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
        Path(Config.LOG_DIR).mkdir(parents=True, exist_ok=True)
