"""
LLM Call - Functions to call LLM and Agent Graph
"""

from typing import List, Optional
from langchain_core.messages import HumanMessage, AnyMessage
from app.llm_functions.LLMDefination import ModelCapability, get_chat_llm
from app.llm_functions.AgentGraph import agentgraph
from app.core.utils import get_logger, trace_llm_call, add_span_attributes

logger = get_logger(__name__)


@trace_llm_call(operation_name="llm.direct_call", capture_args=True)
def CallLLM(query: str, capability: ModelCapability = ModelCapability.BASIC, mcp_tools=None):
    """
    Direct LLM call without agent graph.
    
    Args:
        query: User query string
        capability: Model capability type
        mcp_tools: Optional tools for MCP
        
    Returns:
        LLM response
    """
    logger.info(f"Calling LLM with query: {query}")
    
    # Add capability to trace
    add_span_attributes({
        "llm.capability": capability.value,
        "llm.query_length": len(query),
        "llm.has_mcp_tools": mcp_tools is not None
    })
    
    llm = get_chat_llm(capability)
    response = llm.invoke(query)
    
    # Add response metadata
    add_span_attributes({
        "llm.response_length": len(response.content) if hasattr(response, 'content') else 0
    })
    
    return response


@trace_llm_call(operation_name="llm.agent_graph", capture_args=True)
async def CallAgentGraph(
    query: str,
    chat_id: int,
    history: Optional[List[AnyMessage]] = None
):
    """
    Call agent graph with user query and chat context.
    Processes query through guardrail and synthesis agents.
    
    Args:
        query: User query string
        chat_id: Unique chat identifier (used as LangGraph thread_id)
        history: Optional list of previous messages for context
        
    Returns:
        Final response from the agent graph
    """
    logger.info(f"Calling Agent Graph with query: {query}, chat_id: {chat_id}")
    
    # Add query metadata to trace
    add_span_attributes({
        "agent.query_length": len(query),
        "agent.chat_id": chat_id,
        "agent.thread_id": str(chat_id),
        "agent.history_length": len(history) if history else 0
    })
    
    # Use chat_id as the unique thread identifier for LangGraph
    config = {"configurable": {"thread_id": str(chat_id)}}
    
    # Build inputs: if history is provided, use it; otherwise start fresh
    if history:
        # Append the new query to the existing history
        inputs = {
            "chat_id": chat_id,
            "messages": history + [HumanMessage(content=query)]
        }
    else:
        # Start a new conversation
        inputs = {
            "chat_id": chat_id,
            "messages": [HumanMessage(content=query)]
        }
    
    try:
        response = await agentgraph.ainvoke(inputs, config=config)
        final_response = response['messages'][-1].content.strip()
        
        # Add response metadata
        add_span_attributes({
            "agent.response_length": len(final_response),
            "agent.message_count": len(response['messages']),
            "agent.status": "success"
        })
        
        logger.info(f"Agent Graph response for chat {chat_id}: {final_response}")
        return final_response
    except Exception as e:
        add_span_attributes({
            "agent.status": "error",
            "agent.error": str(e)
        })
        logger.error(f"Error in Agent Graph for chat {chat_id}: {str(e)}", exc_info=True)
        raise
