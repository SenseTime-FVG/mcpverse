
import json
import pandas as pd
import asyncio
from .utils import get_node_res  


import re
from datetime import datetime, timedelta

question = "What is the earnings calendar for Apple Inc.?"



def get_reference():
 

    node = [{"mcp": "alphavantage", "id": "q1", "tool": "earnings_calendar", "args": {"symbol": "AAPL"}}]
    res= asyncio.run(get_node_res(node))['q1']
    reference = f"{res}"
    return reference
