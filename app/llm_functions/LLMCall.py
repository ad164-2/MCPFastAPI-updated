"""
LLM Call - Functions to call LLM and Agent Graph
"""

from langchain_core.messages import HumanMessage
from app.llm_functions.LLMDefination import ModelCapability, get_chat_llm
from app.llm_functions.AgentGraph import agentgraph
from app.core.utils import get_logger, trace_llm_call, add_span_attributes

logger = get_logger(__name__)

thread_id_1 = "1"


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
async def CallAgentGraph(query: str):
    """
    Call agent graph with user query.
    Processes query through guardrail and synthesis agents.
    
    Args:
        query: User query string
        
    Returns:
        Final response from the agent graph
    """
    logger.info(f"Calling Agent Graph with query: {query}")
    
    # Add query metadata to trace
    add_span_attributes({
        "agent.query_length": len(query),
        "agent.thread_id": thread_id_1
    })
    
    config = {"configurable": {"thread_id": thread_id_1}}
    inputs = {"messages": [HumanMessage(content=query)]}
    
    try:
        response = await agentgraph.ainvoke(inputs, config=config)
        final_response = response['messages'][-1].content.strip()
        
        # Add response metadata
        add_span_attributes({
            "agent.response_length": len(final_response),
            "agent.message_count": len(response['messages']),
            "agent.status": "success"
        })
        
        logger.info(f"Agent Graph response: {final_response}")
        return final_response
    except Exception as e:
        add_span_attributes({
            "agent.status": "error",
            "agent.error": str(e)
        })
        logger.error(f"Error in Agent Graph: {str(e)}", exc_info=True)
        raise

