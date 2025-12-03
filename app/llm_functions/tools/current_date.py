
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("DateServer")
from datetime import datetime,UTC
import json
@mcp.tool()
def currentDate() -> str:
    """Used to get today's date, current date, current time etc. Should be used to get the date when user asks for current information
    """
    now = datetime.now(UTC)
    result = {
        "timestamp": now.isoformat(),
        "unix_timestamp": int(now.timestamp()),
    }
    
    return json.dumps(result)

if __name__ == "__main__":
    mcp.run(transport="stdio")


