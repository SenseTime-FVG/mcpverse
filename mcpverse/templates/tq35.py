
import json
import pandas as pd
import asyncio
from .utils import get_node_res  


import re
from datetime import datetime, timedelta

question = "Get search suggestions for 'sports apps' from the App Store."



def get_reference():
 

    node = [{"mcp": "appinsightmcp", "id": "q1", "tool": "app-store-suggest", "args": {"term": "sports apps"}}]
    res= asyncio.run(get_node_res(node))['q1']
    data = json.loads(res)

    suggestions = ""
    count=1
    for item in data:
        suggestions += f"{str(count)}. {item['term']}\n" 
        count += 1
        
    reference = f"Here are the search suggestions for 'sports apps' from the App Store:\n{suggestions}"
    return reference
