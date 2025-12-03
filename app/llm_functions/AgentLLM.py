"""
Agent LLM - Provides LLM instances for the agent graph
"""

from app.llm_functions.LLMDefination import get_chat_llm, ModelCapability
from app.core.utils import get_logger

logger = get_logger(__name__)


def get_base_llm():
    """
    Get base LLM for general responses.
    Uses BASIC capability for simple text generation.
    """
    logger.info("Initializing Base LLM")
    return get_chat_llm(capability=ModelCapability.BASIC)


def get_reasoning_llm():
    """
    Get reasoning LLM for complex logic and validation.
    Uses REASONING capability for advanced analysis.
    """
    logger.info("Initializing Reasoning LLM")
    return get_chat_llm(capability=ModelCapability.REASONING)






