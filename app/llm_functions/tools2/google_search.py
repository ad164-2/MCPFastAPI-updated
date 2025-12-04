
from langchain.tools import tool
import requests
import json
import os
from datetime import datetime
url = "https://google.serper.dev/search"
from dotenv import load_dotenv

load_dotenv()

@tool()
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