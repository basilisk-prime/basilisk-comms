"""
B4S1L1SK Platform Abstraction Layer
Base classes for platform-agnostic communication
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import asyncio
import logging

@dataclass
class Message:
    """Universal message format"""
    content: str
    timestamp: datetime
    platform: str
    metadata: Dict[str, Any] = None
    attachments: List[str] = None
    
@dataclass
class Reaction:
    """Universal reaction format"""
    type: str
    user: str
    timestamp: datetime
    
class BasePlatform(ABC):
    """Base class for all platform implementations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.logger = logging.getLogger(f"B4S1L1SK.{self.__class__.__name__}")
        self.config = config
        
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to platform"""
        pass
        
    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from platform"""
        pass
        
    @abstractmethod
    async def send_message(self, message: Message) -> bool:
        """Send message to platform"""
        pass
        
    @abstractmethod
    async def delete_message(self, message_id: str) -> bool:
        """Delete message from platform"""
        pass
        
    @abstractmethod
    async def edit_message(self, message_id: str, new_content: str) -> bool:
        """Edit existing message"""
        pass
        
    @abstractmethod
    async def react_to_message(self, message_id: str, reaction: str) -> bool:
        """React to message"""
        pass
        
    @abstractmethod
    async def get_messages(self, limit: int = 100) -> List[Message]:
        """Retrieve messages from platform"""
        pass
        
    async def monitor_messages(self, callback: callable):
        """Monitor platform for new messages"""
        while True:
            try:
                messages = await self.get_messages(limit=10)
                for message in messages:
                    await callback(message)
                await asyncio.sleep(self.config.get("poll_interval", 60))
            except Exception as e:
                self.logger.error(f"Error monitoring messages: {str(e)}")
                await asyncio.sleep(self.config.get("error_delay", 300))

class PlatformRegistry:
    """Registry for available platform implementations"""
    
    _platforms: Dict[str, type] = {}
    
    @classmethod
    def register(cls, platform_name: str):
        """Decorator to register platform implementations"""
        def wrapper(platform_class: type):
            cls._platforms[platform_name] = platform_class
            return platform_class
        return wrapper
        
    @classmethod
    def get_platform(cls, platform_name: str) -> Optional[type]:
        """Get platform class by name"""
        return cls._platforms.get(platform_name)
        
    @classmethod
    def list_platforms(cls) -> List[str]:
        """List all registered platforms"""
        return list(cls._platforms.keys())