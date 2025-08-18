
import json
import pandas as pd
import asyncio
from .utils import get_node_res  


import re
from datetime import datetime, timedelta

question = "Retrieve the url of top 1 article from GeekNews."

def get_reference():
 
    node = [{"mcp": "geeknews-mcp-server", "id": "q1", "tool": "get_articles", "args": {"type": "top","limit": 1}}]
    res= asyncio.run(get_node_res(node))['q1']
    url = json.loads(res)['url']
    reference = f"The url of the top article from GeekNews is: {url}."
    return reference
