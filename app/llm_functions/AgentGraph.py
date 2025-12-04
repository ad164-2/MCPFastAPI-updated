"""
Agent Graph - LangGraph workflow with two sample agents for testing
1. Guardrail Agent - Validates and checks input constraints
2. Synthesize Response Agent - Generates the final response
Integrates with MCP tools for extended functionality
"""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from typing_extensions import Literal
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from app.llm_functions.AgentState import AgentState
from app.llm_functions.AgentLLM import get_base_llm, get_reasoning_llm
from app.core.utils import get_logger, trace_llm_operation, add_span_attributes
from app.llm_functions.MCPHelper import GetMCPConfig,InvokeLLMWithMCP
from app.llm_functions.ToolHelper import InvokeLLMWithTool
logger = get_logger(__name__)


async def guardrail_agent(state: AgentState) -> dict:
    """
    Guardrail Agent - Validates input and checks basic constraints.
    This agent ensures the query is valid and safe to process.
    """
    with trace_llm_operation(
        "agent.guardrail",
        attributes={
            "agent.name": "guardrail",
            "agent.type": "validation"
        }
    ):
        logger.info("--- Executing Guardrail Agent ---")
        messages = state["messages"]
        
        guardrail_prompt = SystemMessage(
            content="""You are a guardrail agent. Your job is to validate the user's query.
            Check if the query is:
            1. Not empty or nonsensical
            2. Safe to process
            3. In a reasonable length
            
            Respond with ONLY one word: 'pass' if the query is valid and safe.
            Respond with ONLY one word: 'fail' if the query is invalid, offensive, or unsafe."""
        )
        
        latest_query = messages[-1]
        validation_messages = [guardrail_prompt, latest_query]
        
        add_span_attributes({
            "agent.query_content": str(latest_query.content)[:100],  # First 100 chars
            "agent.message_count": len(messages)
        })
        
        validation_result = get_reasoning_llm().invoke(validation_messages).content.strip().lower()
        logger.info(f"Guardrail validation result: {validation_result}")
        
        add_span_attributes({
            "agent.validation_result": validation_result,
            "agent.status": "pass" if validation_result == "pass" else "fail"
        })
        
        return {"guardrail_status": validation_result}


async def route_guardrail(state: AgentState) -> Literal["synthesize", "reject"]:
    """
    Conditional Edge: Routes based on guardrail validation.
    """
    status = state.get("guardrail_status", "fail")
    return "synthesize" if status == "pass" else "reject"


async def synthesize_response_agent(state: AgentState) -> dict:
    """
    Synthesize Response Agent - Generates the final response to the user query.
    This agent creates a comprehensive and helpful response.
    May use MCP tools if needed.
    """
    with trace_llm_operation(
        "agent.synthesize",
        attributes={
            "agent.name": "synthesize",
            "agent.type": "response_generation"
        }
    ):
        logger.info("--- Executing Synthesize Response Agent ---")
        messages = state["messages"]
        mcpConfig=await GetMCPConfig()
        synthesis_prompt = SystemMessage(
            content="""You are a helpful response synthesis agent. Your job is to generate a clear, 
            concise, and helpful response to the user's query. 
            Keep the response professional and informative.
            
            If you need to access current date/time or database information, you can use available tools."""
        )
        
        synthesis_messages = [synthesis_prompt] + messages
        llm = get_base_llm()
        llmcallinput=  {"messages": synthesis_messages}
        
        add_span_attributes({
            "agent.message_count": len(synthesis_messages),
            "agent.has_mcp_tools": True
        })
        
        #if using MCP
        # response =await InvokeLLMWithMCP(llm,llmcallinput,mcpConfig)
        # if  isinstance(response,list):
        #     response=response[0]['text']

        response= await InvokeLLMWithTool(llm,messages,['CurrentDate','Search'])

        #response = get_base_llm().invoke(synthesis_messages).content.strip()
        logger.info(f"Generated response: {response}")
        
        add_span_attributes({
            "agent.response_length": len(response),
            "agent.status": "success"
        })
        
        return {"messages": state["messages"] + [SystemMessage(content=response)]}


async def reject_query(state: AgentState) -> dict:
    """
    Reject invalid or unsafe queries.
    """
    with trace_llm_operation(
        "agent.reject",
        attributes={
            "agent.name": "reject",
            "agent.type": "rejection"
        }
    ):
        logger.info("--- Rejecting invalid query ---")
        reject_message = SystemMessage(
            content="Your query did not pass validation. Please ensure your input is valid and try again."
        )
        
        add_span_attributes({
            "agent.status": "rejected"
        })
        
        return {"messages": state["messages"] + [reject_message]}

# Build the workflow
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("guardrail_agent", guardrail_agent)
workflow.add_node("synthesize_response_agent", synthesize_response_agent)
workflow.add_node("reject_query", reject_query)

# Set start edge
workflow.add_edge(START, "guardrail_agent")

# Add conditional edges
workflow.add_conditional_edges(
    "guardrail_agent",
    route_guardrail,
    {
        "synthesize": "synthesize_response_agent",
        "reject": "reject_query",
    }
)

# Add end edges
workflow.add_edge("synthesize_response_agent", END)
workflow.add_edge("reject_query", END)

# Compile with checkpointer
checkpointer = InMemorySaver()
agentgraph = workflow.compile(checkpointer=checkpointer)

