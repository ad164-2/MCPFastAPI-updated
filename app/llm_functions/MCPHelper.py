import asyncio
import json
async def GetMCPConfig():
    f=open('./app/llm_functions/mcp_config.json')
    content=f.read()
    return content

async def InvokeLLMWithMCP(llm,messages,mcpconfig):
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
    from langchain_mcp_adapters.client import MultiServerMCPClient
    from langgraph.prebuilt import create_react_agent
    mcpconfig=json.loads(mcpconfig)
    client= MultiServerMCPClient( mcpconfig )
    tools = await client.get_tools()
    agent = create_react_agent(llm,tools,debug=True)
    resp =await agent.ainvoke(
           messages
            )
    responeMessage=GetResponseValue(resp['messages'][-1])
    return responeMessage