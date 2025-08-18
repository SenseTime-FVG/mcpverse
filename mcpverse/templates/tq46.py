
import json
import pandas as pd
import asyncio
from .utils import get_node_res  


import re
from datetime import datetime, timedelta

question = "What is the current exchange rate between USD and EUR?"



def get_reference():
 

    node = [{"mcp": "alphavantage", "id": "q1", "tool": "exchange_rate", "args": {"from_currency": "USD", "to_currency": "EUR"}}]
    res= asyncio.run(get_node_res(node))['q1']
    data=json.loads(res)
    exchange_rate = data['Realtime Currency Exchange Rate']['5. Exchange Rate']
    exchange_rate = "{:.4f}".format(float(exchange_rate))
    reference = "The current exchange rate between USD and EUR is " + exchange_rate + "."
    return reference
