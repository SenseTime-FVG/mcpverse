
import json
import pandas as pd
import asyncio
from .utils import get_node_res  


import re
from datetime import datetime, timedelta

question = 'Show me the urls of the top 3 search result of "Harvard University" in bingcn.'

def get_reference():
 
    node = [{"mcp": "bingcn", "id": "q1", "tool": "bing_search", "args": {"query": "Harvard University","num_results": 3}}]
    res= asyncio.run(get_node_res(node))['q1']
    infos=json.loads(res)
    url1= infos[0]['link']
    url2= infos[1]['link']
    url3= infos[2]['link']
    
    reference = f"The urls of the top 3 articles from BingCN are: {url1}, {url2}, and {url3}."
    return reference
