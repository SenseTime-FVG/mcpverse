
import json
import pandas as pd
import asyncio
from .utils import get_node_res  


import re
from datetime import datetime, timedelta

question = "What is the id of the first result of searching users with keyword 'Nvidia' in Weibo?"



def get_reference():
 

    node = [{"mcp": "weibo", "id": "q1", "tool": "search_users", "args": {"keyword": "Nvidia", "limit": 1, "page": 1}}]
    res= asyncio.run(get_node_res(node))['q1']
    data=json.loads(res)
    id= data[0]['id']
    reference= "The id of the first result of searching users with keyword 'Nvidia' in Weibo is: " + str(id)
    return reference
