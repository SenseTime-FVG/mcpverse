
import json
import pandas as pd
import asyncio
from .utils import get_node_res  


import re
from datetime import datetime, timedelta

question = "Which stock symbols are the top 3 gainers today?"


def get_reference():
 
    node = [{"mcp": "alphavantage", "id": "q1", "tool": "top_gainers_losers", "args": {}}]
    res= asyncio.run(get_node_res(node))['q1']
   
    data = json.loads(res)
    top_gainers = data['top_gainers']
    top_gainer_1 = top_gainers[0]["ticker"]
    top_gainer_2 = top_gainers[1]["ticker"]
    top_gainer_3 = top_gainers[2]["ticker"]
    reference = f"The top 3 gainers today are: {top_gainer_1}, {top_gainer_2}, and {top_gainer_3}."
    return reference
