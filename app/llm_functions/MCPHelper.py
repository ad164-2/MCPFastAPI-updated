import asyncio
import json
from app.core.utils import trace_llm_operation, add_span_attributes

async def GetMCPConfig():
    f=open('./app/llm_functions/mcp_config.json')
    content=f.read()
    return content

async def InvokeLLMWithMCP(llm,messages,mcpconfig):
    """Invoke LLM with MCP tools integration."""
    with trace_llm_operation(
        "llm.mcp.invoke",
        attributes={
            "mcp.enabled": True,
            "mcp.config_loaded": mcpconfig is not None
        }
    ):
        loop = asyncio.get_event_loop()
        executeTask = loop.create_task(
            InvokeLLMWithMCPInner(llm,messages,mcpconfig)
        )
        response = await executeTask
        return response

def GetResponseValue(response):
    if isinstance(response, str):
        return response
    elif hasattr(response, "content"):
        return response.content
    else:
        return response
        
async def InvokeLLMWithMCPInner(llm,messages,mcpconfig):
    """Inner function to create and invoke React agent with MCP tools."""
    with trace_llm_operation(
        "llm.mcp.react_agent",
        attributes={
            "agent.type": "react",
            "mcp.tools_enabled": True
        }
    ):
        from langchain_mcp_adapters.client import MultiServerMCPClient
        from langgraph.prebuilt import create_react_agent
        mcpconfig=json.loads(mcpconfig)
        client= MultiServerMCPClient( mcpconfig )
        tools = await client.get_tools()
        
        add_span_attributes({
            "mcp.tool_count": len(tools),
            "mcp.servers": list(mcpconfig.keys()) if isinstance(mcpconfig, dict) else []
        })
        
        agent = create_react_agent(llm,tools,debug=True)
        resp =await agent.ainvoke(
               messages
                )
        responeMessage=GetResponseValue(resp['messages'][-1])
        
        add_span_attributes({
            "mcp.response_length": len(str(responeMessage))
        })
        
        return responeMessage