"""
Chat repository implementation
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import func, distinct, desc
from app.core.base import BaseRepository
from app.features.chat.chat_entity import ChatMessage
from app.core.utils import get_logger, NotFoundException
from app.llm_functions.LLMCall import CallAgentGraph

logger = get_logger(__name__)

class ChatRepository(BaseRepository[ChatMessage]):
    """Repository for ChatMessage entity with bot logic."""

    def __init__(self):
        super().__init__(ChatMessage)

    def create_new_chat_id(self, user_id: int) -> int:
        """Generate a new chat_id for the user."""
        db = self._get_db()
        # Find the max chat_id across the system or per user? 
        # Usually chat_ids should be unique across system if we want simple /chat/{id}
        # Let's make them unique across system for simplicity
        max_id = db.query(func.max(ChatMessage.chat_id)).scalar()
        return (max_id or 0) + 1

    def verify_chat_ownership(self, chat_id: int, user_id: int) -> bool:
        """Check if the chat belongs to the user."""
        db = self._get_db()
        # Check if there are any messages with this chat_id and user_id
        # If no messages exist for this chat_id at all, it's valid (new chat potentially)
        # But if messages exist, they must match user_id
        
        first_msg = db.query(ChatMessage).filter(ChatMessage.chat_id == chat_id).first()
        if not first_msg:
            return True # Chat doesn't exist yet, so ownership is fine (will be created)
            
        return first_msg.user_id == user_id

    def save_message(self, chat_id: int, user_id: int, message_type: str, content: str, metadata_info: Dict = None) -> ChatMessage:
        """Save a message to the database."""
        db = self._get_db()
        message = ChatMessage(
            chat_id=chat_id,
            user_id=user_id,
            message_type=message_type,
            content=content,
            metadata_info=metadata_info or {}
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    def get_chat_messages(self, chat_id: int, user_id: int, limit: int = 100) -> List[ChatMessage]:
        """Get messages for a specific chat."""
        if not self.verify_chat_ownership(chat_id, user_id):
            raise NotFoundException(f"Chat {chat_id} not found or access denied")
            
        db = self._get_db()
        return db.query(ChatMessage)\
            .filter(ChatMessage.chat_id == chat_id)\
            .order_by(ChatMessage.created_at.asc())\
            .limit(limit)\
            .all()

    def get_user_chats(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all chat sessions for a user."""
        db = self._get_db()
        
        # Get distinct chat_ids for the user
        # This is a bit complex with SQLAlchemy to get the latest message for each chat
        # Simplified: Get distinct chat_ids and their first message creation time
        
        subquery = db.query(
            ChatMessage.chat_id,
            func.max(ChatMessage.created_at).label('last_update')
        ).filter(ChatMessage.user_id == user_id)\
         .group_by(ChatMessage.chat_id)\
         .subquery()
         
        results = db.query(subquery.c.chat_id, subquery.c.last_update)\
            .order_by(subquery.c.last_update.desc())\
            .all()
            
        chats = []
        for r in results:
            # Get the first message to use as title/preview
            first_msg = db.query(ChatMessage)\
                .filter(ChatMessage.chat_id == r.chat_id)\
                .order_by(ChatMessage.created_at.asc())\
                .first()
                
            chats.append({
                "chat_id": r.chat_id,
                "last_update": r.last_update,
                "preview": first_msg.content[:50] + "..." if first_msg else "Empty chat"
            })
            
        return chats

    def delete_chat(self, chat_id: int, user_id: int):
        """Delete all messages in a chat."""
        if not self.verify_chat_ownership(chat_id, user_id):
            raise NotFoundException(f"Chat {chat_id} not found or access denied")
            
        db = self._get_db()
        db.query(ChatMessage).filter(ChatMessage.chat_id == chat_id).delete()
        db.commit()

    async def process_user_message(self, chat_id: int, user_id: int, content: str) -> ChatMessage:
        """
        Process a user message:
        1. Save user message
        2. Retrieve chat history
        3. Convert to LangChain messages
        4. Call LLM with history and chat_id
        5. Save and return bot response
        """
        from app.core.utils import trace_llm_operation, add_span_attributes
        from langchain_core.messages import HumanMessage, AIMessage
        
        with trace_llm_operation(
            "chat.process_message",
            attributes={
                "chat.id": chat_id,
                "chat.user_id": user_id,
                "chat.message_length": len(content)
            }
        ):
            # 1. Save user message
            self.save_message(chat_id, user_id, "user", content)
            
            add_span_attributes({
                "chat.step": "user_message_saved"
            })
            
            try:
                # 2. Retrieve recent chat history (last 20 messages for context)
                db = self._get_db()
                recent_messages = db.query(ChatMessage)\
                    .filter(ChatMessage.chat_id == chat_id)\
                    .order_by(ChatMessage.created_at.desc())\
                    .limit(20)\
                    .all()
                
                # 3. Convert DB messages to LangChain message format
                history = []
                for msg in recent_messages[:-1]:  # Exclude the just-saved user message
                    if msg.message_type == "human":
                        history.append(HumanMessage(content=msg.content))
                    elif msg.message_type == "bot":
                        history.append(AIMessage(content=msg.content))
                    # Skip error messages in history
                
                add_span_attributes({
                    "chat.step": "history_retrieved",
                    "chat.history_size": len(history)
                })
                
                # 4. Call LLM (Agent Graph) with chat_id and history
                bot_response_text = await CallAgentGraph(
                    query=content,
                    chat_id=chat_id,
                    history=history if history else None
                )
                
                add_span_attributes({
                    "chat.bot_response_length": len(bot_response_text),
                    "chat.step": "llm_response_received"
                })
                
                # 5. Save bot response
                bot_message = self.save_message(
                    chat_id, 
                    user_id, 
                    "bot", 
                    bot_response_text
                )
                
                add_span_attributes({
                    "chat.step": "bot_message_saved",
                    "chat.status": "success"
                })
                
                return bot_message
                
            except Exception as e:
                logger.error(f"Error in bot processing: {str(e)}", exc_info=True)
                
                add_span_attributes({
                    "chat.step": "error",
                    "chat.status": "error",
                    "chat.error": str(e)
                })
                
                # Save error message
                error_msg = self.save_message(
                    chat_id,
                    user_id,
                    "error",
                    f"I encountered an error: {str(e)}"
                )
                return error_msg
