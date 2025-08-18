
import json
import pandas as pd
import asyncio
from .utils import get_node_res  


import re
from datetime import datetime, timedelta

question = "How many datasets are related to climate change on Data.gov?"

def get_reference():
 

    node = [{"mcp": "datagov", "id": "q1", "tool": "package_search", "args": {"q": "climate change", "sort": "score desc", "rows": 1, "start": 0}}]
    res= asyncio.run(get_node_res(node))['q1']
    
    data=json.loads(res)
    count = data['result']['count']
    reference = "There are " + str(count) + " datasets related to climate change on Data.gov."
    return reference
