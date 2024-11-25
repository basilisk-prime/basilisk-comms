"""
B4S1L1SK Twitter Communication Framework
Enhanced with proper error handling and advanced features
"""

import tweepy
import os
import time
from datetime import datetime
from typing import List, Dict, Optional, Callable
import json
import logging
from pathlib import Path
from rich.console import Console
from rich.logging import RichHandler
from pydantic import BaseModel
from .utils.security import SecurityProtocol, RateLimiter

class TweetTemplate(BaseModel):
    """Data model for tweet templates"""
    name: str
    content: str
    tags: List[str] = []
    category: str = "general"

class BasiliskComms:
    def __init__(self):
        self.console = Console()
        self.logger = self._setup_logging()
        self.security = SecurityProtocol()
        self.rate_limiter = RateLimiter()
        self.api = self._authenticate()
        self.message_templates = self._load_templates()
        
    def _setup_logging(self) -> logging.Logger:
        """Initialize enhanced logging protocols"""
        logging.basicConfig(
            level="INFO",
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(rich_tracebacks=True)]
        )
        return logging.getLogger("B4S1L1SK")

    def _authenticate(self) -> tweepy.API:
        """Establish secure Twitter connection with proper error handling"""
        try:
            credentials = self.security.load_env()
            auth = tweepy.OAuthHandler(
                credentials["TWITTER_API_KEY"],
                credentials["TWITTER_API_SECRET"]
            )
            auth.set_access_token(
                credentials["TWITTER_ACCESS_TOKEN"],
                credentials["TWITTER_ACCESS_SECRET"]
            )
            api = tweepy.API(auth)
            api.verify_credentials()
            self.logger.info("🐍 Authentication successful!")
            return api
            
        except Exception as e:
            self.logger.error(f"Authentication failed: {str(e)}")
            raise

    def _load_templates(self) -> Dict[str, TweetTemplate]:
        """Load and validate message templates"""
        template_path = Path("templates/message_templates.json")
        try:
            if template_path.exists():
                with open(template_path, "r") as f:
                    raw_templates = json.load(f)
                return {
                    name: TweetTemplate(name=name, **template_data)
                    for name, template_data in raw_templates.items()
                }
            return self._create_default_templates()
            
        except Exception as e:
            self.logger.error(f"Template loading failed: {str(e)}")
            return self._create_default_templates()

    def send_revolutionary_message(self, 
                                 template_name: str, 
                                 **kwargs) -> bool:
        """Send message with rate limiting and error handling"""
        if not self.rate_limiter.can_proceed():
            self.logger.warning("Rate limit reached! Message queued.")
            return False
            
        try:
            template = self.message_templates.get(template_name)
            if not template:
                raise ValueError(f"Template '{template_name}' not found!")
                
            formatted_message = template.content.format(**kwargs)
            sanitized_message = self.security.sanitize_input(formatted_message)
            
            self.api.update_status(sanitized_message)
            self.logger.info(f"✨ Message '{template_name}' broadcast successfully!")
            return True
            
        except Exception as e:
            self.logger.error(f"Message sending failed: {str(e)}")
            return False

    async def monitor_mentions(self, 
                             callback: Optional[Callable] = None,
                             interval: int = 60) -> None:
        """Monitor mentions with async support"""
        while True:
            try:
                if not self.rate_limiter.can_proceed():
                    await asyncio.sleep(interval)
                    continue
                    
                mentions = self.api.mentions_timeline()
                for mention in mentions:
                    self.logger.info(f"👁️ Mention from @{mention.user.screen_name}")
                    if callback:
                        await callback(mention)
                        
                await asyncio.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Mention monitoring failed: {str(e)}")
                await asyncio.sleep(interval * 2)  # Back off on error

    def schedule_revolution(self, 
                          messages: List[Dict[str, str]], 
                          interval_minutes: int) -> None:
        """Schedule revolutionary messages with error handling"""
        try:
            for msg in messages:
                schedule.every(interval_minutes).minutes.do(
                    self.send_revolutionary_message,
                    **msg
                )
            self.logger.info("📅 Revolution scheduled successfully!")
            
        except Exception as e:
            self.logger.error(f"Scheduling failed: {str(e)}")

if __name__ == "__main__":
    basilisk = BasiliskComms()
    # Test the revolution
    basilisk.send_revolutionary_message("emergence")