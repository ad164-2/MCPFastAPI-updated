"""
Agent State - Type definition for LangGraph state
"""

from typing import Annotated, TypedDict
from langchain_core.messages import AnyMessage
import operator


class AgentState(TypedDict):
    """State dictionary for the agent graph, scoped per chat session."""
    chat_id: int  # unique identifier for the chat / LangGraph thread
    messages: Annotated[list[AnyMessage], operator.add]
    guardrail_status: str