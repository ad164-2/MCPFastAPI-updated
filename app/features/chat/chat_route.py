"""
Chat API endpoints - WebSocket and REST
"""

from fastapi import APIRouter, status, WebSocket, WebSocketDisconnect, Query, Depends
from fastapi.responses import JSONResponse
from typing import List
from app.features.chat.chat_schemas import (
    WSMessageRequest, 
    WSMessageResponse, 
    ChatSessionPreview, 
    ChatHistoryResponse,
    ChatMessageResponse
)
from app.features.chat.chat_repository import ChatRepository
from app.core.utils import get_logger
import json

logger = get_logger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

# WebSocket Endpoint
@router.websocket("/ws/{user_id}/{chat_id}")
async def chat_websocket(websocket: WebSocket, chat_id: int, user_id: int):
    """
    WebSocket endpoint for real-time chat.
    
    Args:
        chat_id: 0 for new chat, >0 for existing chat
        user_id: User ID (passed as query param since WS doesn't support headers easily in all clients)
    """
    await websocket.accept()
    repo = ChatRepository()
    
    try:
        # Initialize Chat
        current_chat_id = chat_id
        
        if current_chat_id == 0:
            # Create new chat
            current_chat_id = repo.create_new_chat_id(user_id)
            await websocket.send_text(WSMessageResponse(
                type="chat_created",
                content="New chat session created",
                chat_id=current_chat_id
            ).model_dump_json())
            logger.info(f"New chat created: {current_chat_id} for user {user_id}")
        else:
            # Verify existing chat
            if not repo.verify_chat_ownership(current_chat_id, user_id):
                await websocket.send_text(WSMessageResponse(
                    type="error",
                    content="Chat not found or access denied",
                    chat_id=current_chat_id
                ).model_dump_json())
                await websocket.close()
                return
                
            await websocket.send_text(WSMessageResponse(
                type="chat_loaded",
                content=f"Joined chat {current_chat_id}",
                chat_id=current_chat_id
            ).model_dump_json())
            logger.info(f"User {user_id} joined chat {current_chat_id}")

        # Message Loop
        while True:
            data = await websocket.receive_text()
            
            try:
                # Parse message
                message_data = json.loads(data)
                request = WSMessageRequest(**message_data)
                
                if request.type == "ping":
                    await websocket.send_text(WSMessageResponse(
                        type="pong",
                        content="pong",
                        chat_id=current_chat_id
                    ).model_dump_json())
                    continue
                
                # Process User Message
                # 1. Save & Process
                bot_message = await repo.process_user_message(
                    current_chat_id, 
                    user_id, 
                    request.content
                )
                
                # 2. Send Response
                await websocket.send_text(WSMessageResponse(
                    type="response",
                    content=bot_message.content,
                    chat_id=current_chat_id,
                    message_id=bot_message.id
                ).model_dump_json())
                
            except json.JSONDecodeError:
                await websocket.send_text(WSMessageResponse(
                    type="error",
                    content="Invalid JSON format",
                    chat_id=current_chat_id
                ).model_dump_json())
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}", exc_info=True)
                await websocket.send_text(WSMessageResponse(
                    type="error",
                    content=f"Error: {str(e)}",
                    chat_id=current_chat_id
                ).model_dump_json())

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for chat {chat_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}", exc_info=True)
        try:
            await websocket.close()
        except:
            pass


# REST Endpoints

@router.get("/sessions", response_model=List[ChatSessionPreview])
def get_user_sessions(user_id: int = Query(...)):
    """Get all chat sessions for a user."""
    try:
        repo = ChatRepository()
        sessions = repo.get_user_chats(user_id)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=[
                ChatSessionPreview(
                    chat_id=s["chat_id"],
                    last_update=s["last_update"],
                    preview=s["preview"]
                ).model_dump(mode="json") 
                for s in sessions
            ]
        )
    except Exception as e:
        logger.error(f"Error fetching sessions: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Error fetching chat sessions"}
        )


@router.get("/{chat_id}/history", response_model=ChatHistoryResponse)
def get_chat_history(chat_id: int, user_id: int = Query(...)):
    """Get full history of a chat session."""
    try:
        repo = ChatRepository()
        messages = repo.get_chat_messages(chat_id, user_id)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=ChatHistoryResponse(
                chat_id=chat_id,
                messages=[ChatMessageResponse.model_validate(m) for m in messages]
            ).model_dump(mode="json")
        )
    except Exception as e:
        logger.error(f"Error fetching history: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(e)}
        )


@router.delete("/{chat_id}")
def delete_chat(chat_id: int, user_id: int = Query(...)):
    """Delete a chat session."""
    try:
        repo = ChatRepository()
        repo.delete_chat(chat_id, user_id)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"detail": "Chat deleted successfully"}
        )
    except Exception as e:
        logger.error(f"Error deleting chat: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(e)}
        )


@router.get("/health")
def health_check():
    """Health check endpoint for the chat service"""
    logger.info("Chat service health check")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "ok", "service": "chat_websocket"}
    )
