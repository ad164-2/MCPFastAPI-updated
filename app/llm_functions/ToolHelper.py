
import asyncio
import json
from app.core.utils import trace_llm_operation, add_span_attributes
from .tools2.toolsconfig import toolsConfig
from langchain.agents import create_agent

async def InvokeLLMWithTool(llm,messages,toolnames):
    """Invoke LLM with tools integration."""
    with trace_llm_operation(
        "llm.mcp.invoke",
        attributes={
            "mcp.enabled": True,
            "mcp.config_loaded": toolnames is not None
        }
    ):
        tools=[data['value'] for data in toolsConfig if data['key'] in toolnames]
        agent= create_agent(llm,tools)
        response = agent.invoke({"messages":messages})
        finalResponse=response['messages'][-1].content
        print(finalResponse)
        if isinstance(finalResponse,list):
            finalResponse=finalResponse[0]['text']


        return finalResponse.strip().lower()
