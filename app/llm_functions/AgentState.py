"""
Agent State - Type definition for LangGraph state
"""

from typing import Annotated, TypedDict
from langchain_core.messages import AnyMessage
import operator


class AgentState(TypedDict):
    """State dictionary for the agent graph."""
    messages: Annotated[list[AnyMessage], operator.add]
    guardrail_status: str

 