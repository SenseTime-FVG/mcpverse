
import json
import pandas as pd
import asyncio
from .utils import get_node_res  


import re
from datetime import datetime, timedelta

question = "Retrieve free cash flow of Amazon and Apple from the corresponding most-recent quarterly cash-flow statement (expressed in billions of U.S. dollars). For the one with higher free cash flow, provide Tax Rate For Calcs from the corresponding most-recent quarterly income-statement data"


def get_latest_info(data):
    sorted_dates = sorted(data.keys())
    if len(sorted_dates) < 2:
        raise ValueError("Data must have at least two dates.")
    day = sorted_dates[-1]
    info = data[day]
    return day,info



def get_reference():
    symbol_1 = "AMZN"
    symbol_2 = "AAPL"
    

    node_1 = [{"mcp": "yahoo-finance", "id": "q1", "tool": "get_cashflow", "args":{"symbol": symbol_1,"freq": "quarterly"}}]
    res_1= asyncio.run(get_node_res(node_1))['q1']
    data_1=json.loads(res_1)
    day_1, info_1 = get_latest_info(data_1)
    free_cash_flow_1 = info_1.get("Free Cash Flow")/1_000_000_000

    node_2 = [{"mcp": "yahoo-finance", "id": "q2", "tool": "get_cashflow", "args":{"symbol": symbol_2,"freq": "quarterly"}}]
    res_2= asyncio.run(get_node_res(node_2))['q2']
    data_2=json.loads(res_2)
    day_2, info_2 = get_latest_info(data_2)
    free_cash_flow_2 = info_2.get("Free Cash Flow")/1_000_000_000

    if free_cash_flow_1 > free_cash_flow_2:
        higher_symbol = symbol_1
        higher_free_cash_flow = free_cash_flow_1
        lower_symbol = symbol_2
        lower_free_cash_flow = free_cash_flow_2
        node_income = [{"mcp": "yahoo-finance", "id": "q3", "tool": "get_income_statement", "args":{"symbol": symbol_1,"freq": "quarterly"}}]
        

    elif free_cash_flow_1 < free_cash_flow_2:
        higher_symbol = symbol_2
        higher_free_cash_flow = free_cash_flow_2
        lower_symbol = symbol_1
        lower_free_cash_flow = free_cash_flow_1
        node_income = [{"mcp": "yahoo-finance", "id": "q3", "tool": "get_income_statement", "args":{"symbol": symbol_2,"freq": "quarterly"}}]
    else:
        return "Both companies have the same free cash flow."
    res= asyncio.run(get_node_res(node_income))['q3']
    data_income=json.loads(res)
    day, info= get_latest_info(data_income)
    tax_rate = info.get("Tax Rate For Calcs")
    
    reference=f"The free cash flow of {higher_symbol} from its most recent quarterly cash-flow statement is {higher_free_cash_flow:.2f} billion dollars on {day_1}. The free cash flow of {lower_symbol} from its most recent quarterly cash-flow statement is {lower_free_cash_flow:.2f} billion dollars on {day_2}. Thus the one with higher free cash flow is {higher_symbol} with a tax rate of {tax_rate:.2f} on {day}."
    return reference
