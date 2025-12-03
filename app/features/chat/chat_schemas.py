"""
Chat schemas for request/response validation
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# WebSocket Schemas
class WSMessageRequest(BaseModel):
    """Incoming WebSocket message from client."""
    type: str = Field(default="message", description="Message type: message, ping")
    content: str = Field(..., description="Message content")


class WSMessageResponse(BaseModel):
    """Outgoing WebSocket message to client."""
    type: str = Field(..., description="Response type: response, error, chat_created, chat_loaded")
    content: str = Field(..., description="Message content")
    chat_id: int = Field(..., description="Chat Session ID")
    message_id: Optional[int] = Field(None, description="Database Message ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# REST Schemas
class ChatMessageResponse(BaseModel):
    """Schema for a single chat message."""
    id: int
    chat_id: int
    message_type: str
    content: str
    created_at: datetime
    metadata_info: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class ChatSessionPreview(BaseModel):
    """Schema for chat session list item."""
    chat_id: int
    last_update: datetime
    preview: str


class ChatHistoryResponse(BaseModel):
    """Schema for full chat history."""
    chat_id: int
    messages: List[ChatMessageResponse]
