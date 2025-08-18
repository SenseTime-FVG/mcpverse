
import json
import pandas as pd
import asyncio
from .utils import get_node_res  


import re
from datetime import datetime, timedelta

question = 'Show me the paper name and url of the first search result of "mamba out" in google scholar.'

def get_reference():
 
    node = [{"mcp": "google-scholar-mcp-server", "id": "q1", "tool": "search_google_scholar_key_words", "args": {"query": "mamba out","num_results": 3}}]
    res= asyncio.run(get_node_res(node))['q1']

    breakpoint()
    url = json.loads(res)['url']
    reference = f"The url of the top article from GeekNews is: {url}."
    return reference
