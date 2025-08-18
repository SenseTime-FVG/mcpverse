
import json
import pandas as pd
import asyncio
from .utils import get_node_res  


import re
from datetime import datetime, timedelta

question = "How many active moderate weather alerts are there currently in Maine and in Ohio? Which state has more?"



def get_reference():
 
    state1= "ME"
    state2= "OH"
    target="Severity: Moderate"
    node_1= [{"mcp": "weather", "id": "q1", "tool": "get-alerts", "args": {"state": state1}}]
    res_1= asyncio.run(get_node_res(node_1))['q1']
    count_1 = res_1.count(target)

    node_2= [{"mcp": "weather", "id": "q2", "tool": "get-alerts", "args": {"state": state2}}]
    res_2= asyncio.run(get_node_res(node_2))['q2']
    count_2 = res_2.count(target)
    
    if count_1 > count_2:
        reference = f"There are {count_1} active moderate weather alerts in Maine and {count_2} in Ohio. Maine has more."
    elif count_1 < count_2:
        reference = f"There are {count_1} active moderate weather alerts in Maine and {count_2} in Ohio. Ohio has more."
    else:
        reference = f"There are {count_1} active moderate weather alerts in Maine and {count_2} in Ohio. Both states have the same number of alerts."

    return reference
