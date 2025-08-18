
import json
import pandas as pd
import asyncio
from .utils import get_node_res  


import re
from datetime import datetime, timedelta

question = "Retrieve the value of DIS’s latest dividend."


def get_latest_dividend(data):
    sorted_dates = sorted(data.keys())
    if len(sorted_dates) < 2:
        raise ValueError("Data must have at least two dates.")
    day = sorted_dates[-1]
    value = data[day]
    
    return day,value

def get_reference():
    symbol_1 = "DIS"
    node_1 = [{"mcp": "yahoo-finance", "id": "q1", "tool": "get_dividends", "args":{"symbol": symbol_1}}]
    res_1= asyncio.run(get_node_res(node_1))['q1']
    data_1=json.loads(res_1)
    day_1, value_1 = get_latest_dividend(data_1)
    reference = f"The latest dividend for {symbol_1} is ${value_1:.2f} on {day_1}."
    return reference
