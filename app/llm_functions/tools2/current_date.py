
from langchain.tools import tool
from datetime import datetime,UTC
import json

@tool
def currentDate() -> str:
    """Used to get today's date, current date, current time etc. Should be used to get the date when user asks for current information. Date returned is in UTC format.
    """
    now = datetime.now(UTC)
    result = {
        "timestamp": now.isoformat(),
        "unix_timestamp": int(now.timestamp()),
    }
    
    return json.dumps(result)


