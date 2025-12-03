
from mcp.server.fastmcp import FastMCP
import requests
import json
import os
mcp = FastMCP("google_search")
from datetime import datetime
url = "https://google.serper.dev/search"


@mcp.tool()
def search(searchstatement:str) -> str:
    """Used to search the web to get information 
        args:
        searchstatement: The information being searched for in the web
    """
   
    if not "SERPER_API_KEY" in os.environ:
         raise Exception("Serper API key is not defined")
  
    payload = json.dumps({
             "q": searchstatement
         })
    headers = {
         'X-API-KEY':os.environ["SERPER_API_KEY"],
         'Content-Type': 'application/json'
     }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.text

    # response = f'Todays date is {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}'
    # return response
if __name__ == "__main__":
    mcp.run(transport="stdio")