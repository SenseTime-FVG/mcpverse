
import json
import pandas as pd
import asyncio
from .utils import get_node_res  
import re
from datetime import datetime, timezone


question = "How many days are left until Christmas 2025(in UTC)?"



def days_until_christmas(current_iso_utc: str) -> int:

    now = datetime.fromisoformat(current_iso_utc)
    today = now.date()          
    christmas_2025 = datetime(2025, 12, 25, 0, 0, 0, tzinfo=timezone.utc)
    christmas_2025 = christmas_2025.date()
    return (christmas_2025 - today).days

def get_reference():
    node_1 = [{"mcp": "time", "id": "q1", "tool": "get_current_time", "args": {"timezone": "UTC"}}]    
    res_1= asyncio.run(get_node_res(node_1))['q1']
    data_1=json.loads(res_1)
    datetime_1 = data_1['datetime']
    days_left = days_until_christmas(datetime_1)
    reference=f"There are {days_left} days left until Christmas 2025 in UTC.".format(days_left=days_left)
    return reference
