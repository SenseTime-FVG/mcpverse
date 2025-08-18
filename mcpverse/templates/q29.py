
import json
import pandas as pd
import asyncio
from .utils import get_node_res  


import re
from datetime import datetime, timedelta

question = 'What are the wind directions in Beijing and Wuhan during the daytime tomorrow according to Amap? Are they the same?'


def get_reference():
    city1="北京"
    city2="武汉"
    city1_en="Beijing"
    city2_en="Wuhan"
    
    cn_en_directions = {
        "东": "East",
        "西": "West",
        "南": "South",
        "北": "North",
        "东北": "Northeast",
        "西北": "Northwest",
        "东南": "Southeast",
        "西南": "Southwest"
    }


    get_tiem_node = [{"mcp": "amap-maps", "id": "q1", "tool": "maps_weather", "args": {"city": city1}}]
    get_time_res= asyncio.run(get_node_res(get_tiem_node))['q1']
    d1 = json.loads(get_time_res)["forecasts"][1]["daywind"]

    get_tiem_node = [{"mcp": "amap-maps", "id": "q2", "tool": "maps_weather", "args": {"city": city2}}]
    get_time_res= asyncio.run(get_node_res(get_tiem_node))['q2']
    d2 = json.loads(get_time_res)["forecasts"][1]["daywind"]

    if d1 == d2:
        reference = f"Tomorrow, the daytime wind direction in {city1_en} and {city2_en} will be the same, both at {cn_en_directions[d1]}."
    else:
        reference = f"Tomorrow, the daytime wind direction in {city1_en} will be {cn_en_directions[d1]}, while in {city2_en} it will be {cn_en_directions[d2]}. Thus, they are not the same."

    return reference
