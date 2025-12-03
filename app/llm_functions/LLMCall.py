"""
LLM Call - Functions to call LLM and Agent Graph
"""

from langchain_core.messages import HumanMessage
from app.llm_functions.LLMDefination import ModelCapability, get_chat_llm
from app.llm_functions.AgentGraph import agentgraph
from app.core.utils import get_logger

logger = get_logger(__name__)

thread_id_1 = "1"


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
    llm = get_chat_llm(capability)
    response = llm.invoke(query)
    return response


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
    config = {"configurable": {"thread_id": thread_id_1}}
    inputs = {"messages": [HumanMessage(content=query)]}
    
    try:
        response = await agentgraph.ainvoke(inputs, config=config)
        final_response = response['messages'][-1].content.strip()
        logger.info(f"Agent Graph response: {final_response}")
        return final_response
    except Exception as e:
        logger.error(f"Error in Agent Graph: {str(e)}", exc_info=True)
        raise

