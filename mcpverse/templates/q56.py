
import json
import pandas as pd
import asyncio
from .utils import get_node_res  


import re
from datetime import datetime, timedelta

question = "Retrieve Apple’s free cash flow from its most recent quarterly cash-flow statement, expressed in billions of U.S. dollars."


def get_latest_info(data):
    sorted_dates = sorted(data.keys())
    if len(sorted_dates) < 2:
        raise ValueError("Data must have at least two dates.")
    day = sorted_dates[-1]
    info = data[day]
    return day,info



def get_reference():
    symbol_1 = "AAPL"
    node_1 = [{"mcp": "yahoo-finance", "id": "q1", "tool": "get_cashflow", "args":{"symbol": symbol_1,"freq": "quarterly"}}]
    res_1= asyncio.run(get_node_res(node_1))['q1']
    data_1=json.loads(res_1)
    day_1, info_1 = get_latest_info(data_1)
    free_cash_flow = info_1.get("Free Cash Flow")/1_000_000_000 
    reference= f"Apple's free cash flow from its most recent quarterly cash-flow statement is {free_cash_flow:.2f} billion dollars on {day_1}."
    return reference
