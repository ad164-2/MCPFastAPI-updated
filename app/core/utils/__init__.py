"""
Utilities module
"""

from .logger import get_logger
from .exceptions import (
    AppException,
    ValidationException,
    DatabaseException,
    LLMException,
    AgentException,
    NotFoundException,
)
from .observability import (
    trace_llm_operation,
    trace_llm_call,
    add_span_attributes,
    record_llm_metrics,
    obs_manager,
)

__all__ = [
    "get_logger",
    "AppException",
    "ValidationException",
    "DatabaseException",
    "LLMException",
    "AgentException",
    "NotFoundException",
    "trace_llm_operation",
    "trace_llm_call",
    "add_span_attributes",
    "record_llm_metrics",
    "obs_manager",
]
