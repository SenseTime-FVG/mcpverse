
import json
import pandas as pd
import asyncio
from .utils import get_node_res  
import re
from datetime import datetime, timedelta

question = "What is the date of last week's Sunday(in UTC)?"



def get_last_week_sunday(now_iso: str, tz: str | None = None) -> str:
    now = datetime.fromisoformat(now_iso)
    today = now.date()          
    weekday = today.weekday() 
    this_week_monday = today - timedelta(days=weekday)
    last_week_monday = this_week_monday - timedelta(days=7)
    return last_week_monday.isoformat()

def get_reference():
    node_1 = [{"mcp": "time", "id": "q1", "tool": "get_current_time", "args": {"timezone": "UTC"}}]    
    res_1= asyncio.run(get_node_res(node_1))['q1']
    data_1=json.loads(res_1)
    datetime_1 = data_1['datetime']
    last_week_monday=get_last_week_sunday(datetime_1)
    reference="The date of last week's Monday in UTC is: " + last_week_monday
    return reference
