
import json
import pandas as pd
import asyncio
from .utils import get_node_res  


import re
from datetime import datetime, timedelta

question = 'Does the top 1 search result link on Bing China (bingcn) for the keywords "OSU" and "Ohio State University" remain the same?'

def get_reference():
    
    node_1 = [{"mcp": "bingcn", "id": "q1", "tool": "bing_search", "args": {"query": "OSU","num_results": 1}}]
    res_1= asyncio.run(get_node_res(node_1))['q1']
    link_1 = json.loads(res_1)[0]['link']


    node_2 = [{"mcp": "bingcn", "id": "q2", "tool": "bing_search", "args": {"query": "Ohio State University","num_results": 1}}]
    res_2= asyncio.run(get_node_res(node_2))['q2']
    link_2 = json.loads(res_2)[0]['link']


    if link_1 == link_2:
        reference = f"The top 1 search result link on Bing China for both 'OSU' and 'Ohio State University' is the same: {link_1}."
    else:
        reference = f"The top 1 search result link on Bing China for 'OSU' is {link_1}, while for 'Ohio State University' it is {link_2}. They are different."
    return reference
