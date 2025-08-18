
import json
import pandas as pd
import asyncio
from .utils import get_node_res  


import re
from datetime import datetime, timedelta

question = "Which app has more ratings in the US App Store, the one with ID 6446788829 or the one with ID 317469184? "


def calculate_total_ratings(data):    
    """
    Calculate the total number of ratings from the histogram data.
    """
    total_ratings = 0
    for star, count in data['histogram'].items():
        total_ratings += count
    return total_ratings

def get_reference():
 
    ID1= 6446788829
    ID2= 317469184
    node_1= [{"mcp": "appinsightmcp", "id": "q1", "tool": "app-store-ratings", "args": {"id": ID1, "country": "us"}},]
    res_1= asyncio.run(get_node_res(node_1))['q1']
    data_1 = json.loads(res_1)
    rating1=calculate_total_ratings(data_1)


    node_2= [{"mcp": "appinsightmcp", "id": "q2", "tool": "app-store-ratings", "args": {"id": ID2, "country": "us"}},]
    res_2= asyncio.run(get_node_res(node_2))['q2']
    data_2 = json.loads(res_2)
    rating2=calculate_total_ratings(data_2)
    if rating1 > rating2:
        reference = f"The app with ID {ID1} has more ratings ({rating1}) than the app with ID {ID2} ({rating2})."
    elif rating1 < rating2:
        reference = f"The app with ID {ID2} has more ratings ({rating2}) than the app with ID {ID1} ({rating1})."
    else:
        reference = f"Both apps have the same number of ratings: {rating1}."
  

    return reference
