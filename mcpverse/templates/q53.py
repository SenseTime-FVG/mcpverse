
import json
import pandas as pd
import asyncio
from .utils import get_node_res  


import re
from datetime import datetime, timedelta

question = "Compared to the previous closing day, did the last closing price leave me overall up or down if I own one share of AMZN and two share of DIS?"

def convert_price_dict(data):
    sorted_dates = sorted(data.keys())
    if len(sorted_dates) < 2:
        raise ValueError("Data must have at least two dates.")
    
    previous_day = sorted_dates[-2]
    last_day = sorted_dates[-1]
    
    previous_value = data[previous_day]
    last_value = data[last_day]
    
    return (last_day, previous_day, last_value, previous_value)

def get_reference():
    symbol_1 = "AMZN"
    symbol_2 = "DIS"

    node_1 = [{"mcp": "yahoo-finance", "id": "q1", "tool": "get_historical_stock_prices", "args":{"symbol": symbol_1, "period": "2d", "interval": "1d"}}]
    res_1= asyncio.run(get_node_res(node_1))['q1']
    data_1=json.loads(res_1)
    last_day_1, previous_day_1, last_value_1, previous_value_1 = convert_price_dict(data_1)

    node_2 = [{"mcp": "yahoo-finance", "id": "q2", "tool": "get_historical_stock_prices", "args":{"symbol": symbol_2, "period": "2d", "interval": "1d"}}]
    res_2= asyncio.run(get_node_res(node_2))['q2']
    data_2=json.loads(res_2)
    last_day_2, previous_day_2, last_value_2, previous_value_2 = convert_price_dict(data_2)

    # Calculate the total value change
    total_last_value = last_value_1 + last_value_2 * 2
    total_previous_value = previous_value_1 + previous_value_2 * 2
    total_change = total_last_value - total_previous_value

    # Determine if the change is up or down
    if total_change > 0:
        reference= f"Overall up by ${total_change:.2f} compared to the previous closing day."
    elif total_change < 0:
        reference= f"Overall down by ${-total_change:.2f} compared to the previous closing day."
    else:
        reference = "No change compared to the previous closing day."

    return reference
