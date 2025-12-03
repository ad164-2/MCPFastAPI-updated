"""
Chat entity model
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from app.core.base import BaseEntity
from datetime import datetime

class ChatMessage(BaseEntity):
    """
    Chat message entity.
    Stores all messages for all chats.
    chat_id groups messages into conversations.
    """
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, index=True, nullable=False)
    user_id = Column(Integer, nullable=False, index=True)  # No ForeignKey, just storing the ID
    message_type = Column(String(50), nullable=False)  # user, bot, system, error
    content = Column(Text, nullable=False)
    metadata_info = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, chat_id={self.chat_id}, type={self.message_type})>"
