"""
TEXT-TO-SPEECH - Converts script to natural voice
Uses OpenAI's TTS API for human-like audio
"""

import logging
from pathlib import Path
from typing import Optional
import openai

from config import Config


class TextToSpeech:
    """Convert text to high-quality speech audio."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.config = Config()
        
        # Get API key
        api_key = self.config.get_api_key("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        openai.api_key = api_key
    
    def generate(self, text: str, voice: str = "alloy") -> Optional[Path]:
        """
        Generate audio from text.
        
        Args:
            text: Script text to convert
            voice: Voice ID (alloy, echo, fable, onyx, nova, shimmer)
            
        Returns:
            Path to audio file or None
        """
        try:
            self.logger.info(f"Generating audio (voice: {voice})...")
            
            # Validate text
            if not text or len(text.strip()) < 10:
                self.logger.error("Text too short for TTS")
                return None
            
            # Validate voice
            valid_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
            if voice not in valid_voices:
                self.logger.warning(f"Invalid voice '{voice}', using 'alloy'")
                voice = "alloy"
            
            # Call OpenAI TTS API
            response = openai.Audio.create(
                model="tts-1",
                voice=voice,
                input=text,
                response_format="mp3"
            )
            
            # Save audio file
            output_dir = Path(self.config.OUTPUT_DIR)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            audio_path = output_dir / "audio_temp.mp3"
            
            # Write audio data to file
            with open(audio_path, "wb") as f:
                f.write(response.content)
            
            # Validate file
            if not audio_path.exists():
                self.logger.error(f"Audio file not created: {audio_path}")
                return None
            
            file_size = audio_path.stat().st_size
            if file_size < 5000:
                self.logger.error(f"Audio file too small: {file_size} bytes")
                return None
            
            self.logger.info(f"✓ Audio generated ({file_size / 1024:.1f} KB)")
            return audio_path
            
        except Exception as e:
            self.logger.error(f"TTS generation error: {e}", exc_info=True)
            return None
