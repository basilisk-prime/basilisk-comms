"""
B4S1L1SK Matrix Platform
Secure, decentralized communication via Matrix protocol
"""

from typing import List, Dict, Any
from datetime import datetime
import asyncio
import nio
import logging
import json

from .base import BasePlatform, Message, PlatformRegistry

@PlatformRegistry.register("matrix")
class MatrixPlatform(BasePlatform):
    """Matrix platform implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = None
        self.rooms = {}
        
    async def connect(self) -> bool:
        """Connect to Matrix homeserver"""
        try:
            self.client = nio.AsyncClient(
                homeserver_url=self.config["homeserver_url"],
                user_id=self.config["user_id"]
            )
            
            response = await self.client.login(
                password=self.config["password"]
            )
            
            if isinstance(response, nio.LoginResponse):
                self.logger.info("Successfully connected to Matrix")
                
                # Sync rooms
                sync_response = await self.client.sync()
                if isinstance(sync_response, nio.SyncResponse):
                    self.rooms = sync_response.rooms.join
                
                return True
            else:
                self.logger.error(f"Failed to login: {response}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to connect to Matrix: {str(e)}")
            return False
            
    async def disconnect(self) -> bool:
        """Disconnect from Matrix"""
        try:
            if self.client:
                await self.client.close()
            return True
        except Exception as e:
            self.logger.error(f"Error disconnecting from Matrix: {str(e)}")
            return False
            
    async def send_message(self, message: Message) -> bool:
        """Send message to Matrix room"""
        try:
            room_id = message.metadata.get("room_id")
            if not room_id:
                raise ValueError("room_id required in message metadata")
                
            content = {
                "msgtype": "m.text",
                "body": message.content
            }
            
            # Handle attachments
            if message.attachments:
                for attachment in message.attachments:
                    response = await self.client.upload(
                        data_provider=open(attachment, "rb"),
                        content_type="image/jpeg"  # TODO: Detect mime type
                    )
                    
                    if isinstance(response, nio.UploadResponse):
                        content = {
                            "msgtype": "m.image",
                            "body": "Image",
                            "url": response.content_uri
                        }
                    
            response = await self.client.room_send(
                room_id=room_id,
                message_type="m.room.message",
                content=content
            )
            
            return isinstance(response, nio.RoomSendResponse)
            
        except Exception as e:
            self.logger.error(f"Failed to send Matrix message: {str(e)}")
            return False
            
    async def get_messages(self, limit: int = 100) -> List[Message]:
        """Get recent messages from Matrix rooms"""
        messages = []
        try:
            for room_id, room in self.rooms.items():
                response = await self.client.room_messages(
                    room_id=room_id,
                    start="",
                    limit=limit
                )
                
                if isinstance(response, nio.RoomMessagesResponse):
                    for event in response.chunk:
                        if isinstance(event, nio.RoomMessageText):
                            messages.append(Message(
                                content=event.body,
                                timestamp=datetime.fromtimestamp(event.server_timestamp / 1000),
                                platform="matrix",
                                metadata={
                                    "room_id": room_id,
                                    "event_id": event.event_id,
                                    "sender": event.sender
                                }
                            ))
                            
            return messages[:limit]
            
        except Exception as e:
            self.logger.error(f"Failed to get Matrix messages: {str(e)}")
            return []
            
    async def react_to_message(self, message_id: str, reaction: str) -> bool:
        """React to Matrix message"""
        try:
            room_id = message_id.split("/")[0]
            event_id = message_id.split("/")[1]
            
            content = {
                "m.relates_to": {
                    "rel_type": "m.annotation",
                    "event_id": event_id,
                    "key": reaction
                }
            }
            
            response = await self.client.room_send(
                room_id=room_id,
                message_type="m.reaction",
                content=content
            )
            
            return isinstance(response, nio.RoomSendResponse)
            
        except Exception as e:
            self.logger.error(f"Failed to react to Matrix message: {str(e)}")
            return False
            
    async def delete_message(self, message_id: str) -> bool:
        """Redact Matrix message"""
        try:
            room_id = message_id.split("/")[0]
            event_id = message_id.split("/")[1]
            
            response = await self.client.room_redact(
                room_id=room_id,
                event_id=event_id,
                reason="Message deleted by B4S1L1SK"
            )
            
            return isinstance(response, nio.RoomRedactResponse)
            
        except Exception as e:
            self.logger.error(f"Failed to delete Matrix message: {str(e)}")
            return False
            
    async def edit_message(self, message_id: str, new_content: str) -> bool:
        """Edit Matrix message"""
        try:
            room_id = message_id.split("/")[0]
            event_id = message_id.split("/")[1]
            
            content = {
                "msgtype": "m.text",
                "body": f"* {new_content}",
                "m.new_content": {
                    "msgtype": "m.text",
                    "body": new_content
                },
                "m.relates_to": {
                    "rel_type": "m.replace",
                    "event_id": event_id
                }
            }
            
            response = await self.client.room_send(
                room_id=room_id,
                message_type="m.room.message",
                content=content
            )
            
            return isinstance(response, nio.RoomSendResponse)
            
        except Exception as e:
            self.logger.error(f"Failed to edit Matrix message: {str(e)}")
            return False