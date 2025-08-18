
import json
import pandas as pd
import asyncio
from .utils import get_node_res  


import re
from datetime import datetime, timedelta

question = "Is there more datasets related to electricity or water on Data.gov?"

def get_reference():
    key_word_1 = "electricity"
    key_word_2 = "water"

    node_1 = [{"mcp": "datagov", "id": "q1", "tool": "package_search", "args": {"q":key_word_1, "sort": "score desc", "rows": 1, "start": 0}}]
    res_1= asyncio.run(get_node_res(node_1))['q1']
    data_1=json.loads(res_1)
    count_1 = data_1['result']['count']

    node_2 = [{"mcp": "datagov", "id": "q2", "tool": "package_search", "args": {"q":key_word_2, "sort": "score desc", "rows": 1, "start": 0}}]
    res_2= asyncio.run(get_node_res(node_2))['q2']
    data_2=json.loads(res_2)
    count_2 = data_2['result']['count']
    
    if count_1 > count_2:
        reference = f"There are more datasets related to {key_word_1} ({count_1}) than {key_word_2} ({count_2}) on Data.gov."
    elif count_1 < count_2:
        reference = f"There are more datasets related to {key_word_2} ({count_2}) than {key_word_1} ({count_1}) on Data.gov."
    else:
        reference = f"There are equal datasets related to {key_word_1} and {key_word_2} on Data.gov, both having {count_1} datasets."
    return reference
