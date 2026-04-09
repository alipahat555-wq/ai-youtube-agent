"""
SCRIPT GENERATOR - Creates unique, viral scripts
Uses OpenAI GPT for intelligent content generation
"""

import logging
import random
from typing import Optional, Dict, List
import openai

from config import Config


class ScriptGenerator:
    """Generate unique viral scripts for different niches."""
    
    # Script templates for different niches
    NICHES = {
        "motivation": {
            "hooks": [
                "Your biggest opponent is yesterday's version of you.",
                "Success doesn't happen overnight. It happens every day.",
                "The only way out is through.",
                "Your potential is limitless.",
                "Don't wait for motivation. Create it.",
            ],
            "topics": [
                "overcoming procrastination",
                "building unstoppable confidence",
                "the power of small daily habits",
                "turning pain into purpose",
                "becoming unstoppable",
            ]
        },
        "asmr": {
            "hooks": [
                "Watch as perfection unfolds.",
                "Smooth. Satisfying. Calming.",
                "Let your mind relax completely.",
                "Pure satisfaction in 60 seconds.",
                "The ultimate satisfying experience.",
            ],
            "topics": [
                "satisfying slicing",
                "mesmerizing patterns",
                "oddly satisfying loops",
                "calming water flows",
                "soothing geometric perfection",
            ]
        },
        "educational": {
            "hooks": [
                "Here's something you didn't know.",
                "This fact will blow your mind.",
                "Learn this in under 60 seconds.",
                "A hidden truth nobody talks about.",
                "Your perspective will change.",
            ],
            "topics": [
                "amazing historical facts",
                "bizarre science discoveries",
                "hidden psychological truths",
                "mind-bending physics",
                "secrets of successful people",
            ]
        }
    }
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.config = Config()
        
        # Get API key
        api_key = self.config.get_api_key("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        openai.api_key = api_key
    
    def generate(self) -> Optional[Dict]:
        """
        Generate complete script package.
        
        Returns:
            Dict with: script, title, description, tags
        """
        try:
            self.logger.info("Generating script...")
            
            # Select niche
            niche = self.config.NICHE
            if niche not in self.NICHES:
                self.logger.warning(f"Unknown niche: {niche}, using 'motivation'")
                niche = "motivation"
            
            # Select random topic from niche
            topic = random.choice(self.NICHES[niche]["topics"])
            hook = random.choice(self.NICHES[niche]["hooks"])
            
            self.logger.info(f"Selected niche: {niche}, topic: {topic}")
            
            # Generate script
            script = self._generate_script(niche, topic, hook)
            if not script:
                return None
            
            # Generate title
            title = self._generate_title(script, niche)
            if not title:
                title = f"{niche.title()} - {topic.title()}"
            
            # Generate description
            description = self._generate_description(script)
            if not description:
                description = f"Amazing {niche} content. Don't miss this!"
            
            # Generate tags
            tags = self._generate_tags(script, niche)
            if not tags:
                tags = [niche, topic.replace(" ", ""), "shorts", "viral"]
            
            result = {
                "script": script,
                "title": title[:100],  # YouTube limit
                "description": description[:5000],  # YouTube limit
                "tags": tags[:30],  # YouTube limit
                "niche": niche,
                "topic": topic,
                "hook": hook
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Script generation error: {e}", exc_info=True)
            return None
    
    def _generate_script(self, niche: str, topic: str, hook: str) -> Optional[str]:
        """Generate the main script using OpenAI."""
        try:
            prompt = f"""Create a short, engaging script for a {niche} YouTube Short (60-100 words).
            
Topic: {topic}
Hook: {hook}

The script should be:
- Compelling and engaging
- Natural-sounding (for text-to-speech)
- No hashtags or emojis
- Just plain text for voice

Script:"""
            
            response = openai.ChatCompletion.create(
                model=self.config.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional YouTube content writer. Create viral, engaging scripts."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            script = response.choices[0].message.content.strip()
            
            if script:
                self.logger.info(f"✓ Script generated ({len(script)} chars)")
                return script
            
            return None
            
        except Exception as e:
            self.logger.error(f"Script generation API error: {e}", exc_info=True)
            return None
    
    def _generate_title(self, script: str, niche: str) -> Optional[str]:
        """Generate catchy title."""
        try:
            prompt = f"""Create a catchy YouTube Shorts title (max 60 characters) for this {niche} script:

"{script[:80]}..."

Title (just the title, nothing else):"""
            
            response = openai.ChatCompletion.create(
                model=self.config.OPENAI_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.8,
                max_tokens=20
            )
            
            title = response.choices[0].message.content.strip()
            return title if title else None
            
        except Exception as e:
            self.logger.warning(f"Title generation failed: {e}")
            return None
    
    def _generate_description(self, script: str) -> Optional[str]:
        """Generate YouTube description."""
        try:
            prompt = f"""Create a YouTube video description (100-150 words) for this script:

"{script[:100]}..."

Description:"""
            
            response = openai.ChatCompletion.create(
                model=self.config.OPENAI_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=100
            )
            
            description = response.choices[0].message.content.strip()
            return description if description else None
            
        except Exception as e:
            self.logger.warning(f"Description generation failed: {e}")
            return None
    
    def _generate_tags(self, script: str, niche: str) -> Optional[List[str]]:
        """Generate YouTube tags."""
        try:
            prompt = f"""Generate 8 relevant YouTube tags (comma-separated) for this {niche} video:

"{script[:80]}..."

Tags (comma-separated, no hashtags):"""
            
            response = openai.ChatCompletion.create(
                model=self.config.OPENAI_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.6,
                max_tokens=50
            )
            
            tags_text = response.choices[0].message.content.strip()
            tags = [tag.strip() for tag in tags_text.split(",")]
            return tags if tags else None
            
        except Exception as e:
            self.logger.warning(f"Tags generation failed: {e}")
            return None
