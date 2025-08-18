
import json
import pandas as pd
import asyncio
from .utils import get_node_res  


import re
from datetime import datetime, timedelta

question = 'Do the top 3 search results for "James Harden" and "Harden" on Bing China (bingcn) have any cross-over?'

def get_reference():
    
    node_1 = [{"mcp": "bingcn", "id": "q1", "tool": "bing_search", "args": {"query": "James Harden","num_results": 3}}]
    res_1= asyncio.run(get_node_res(node_1))['q1']
    link_list_1 = [json.loads(res_1)[i]['link'] for i in range(min(3, len(json.loads(res_1))))]

    node_2 = [{"mcp": "bingcn", "id": "q2", "tool": "bing_search", "args": {"query": "Harden","num_results": 3}}]
    res_2= asyncio.run(get_node_res(node_2))['q2']

    link_list_2 = [json.loads(res_2)[i]['link'] for i in range(min(3, len(json.loads(res_2))))]

    cross_over = set(link_list_1) & set(link_list_2)
    if cross_over:
        reference = f"The top 3 search results for 'James Harden' and 'Harden' on Bing China have the following cross-over links: {', '.join(cross_over)}."
    else:
        reference = "There are no cross-over links between the top 3 search results for 'James Harden' and 'Harden' on Bing China."
    return reference
