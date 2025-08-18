
import json
import pandas as pd
import asyncio
from .utils import get_node_res  


import re
from datetime import datetime, timedelta

question = 'Which city will have a higher night-time temperature tomorrow, Beijing or Wuhan, according to Amap(accurate to whole number)? Also show the temperature of both cities.'




def get_reference():
    city1="北京"
    city2="武汉"
    city1_en="Beijing"
    city2_en="Wuhan"
    
    get_tiem_node = [{"mcp": "amap-maps", "id": "q1", "tool": "maps_weather", "args": {"city": city1}}]
    get_time_res= asyncio.run(get_node_res(get_tiem_node))['q1']
    w1 = int(json.loads(get_time_res)["forecasts"][1]["nighttemp"])

    get_tiem_node = [{"mcp": "amap-maps", "id": "q2", "tool": "maps_weather", "args": {"city": city2}}]
    get_time_res= asyncio.run(get_node_res(get_tiem_node))['q2']
    w2 = int(json.loads(get_time_res)["forecasts"][1]["nighttemp"])

    

    if w1 > w2:
        reference = f"Tomorrow, the night-time temperature in {city1_en} will be higher than that in {city2_en}, with {city1_en} at {w1}°C and {city2_en} at {w2}°C."
    elif w1 < w2:
        reference = f"Tomorrow, the night-time temperature in {city2_en} will be higher than that in {city1_en}, with {city2_en} at {w2}°C and {city1_en} at {w1}°C."
    elif w1 == w2:
        reference = f"Tomorrow, the night-time temperature in {city1_en} and {city2_en} will be the same, both at {w1}°C."

    return reference
