
import json
import pandas as pd
import asyncio
from .utils import get_node_res  


import re
from datetime import datetime, timedelta

question = "Search for Airbnb listings in Paris for 1 adults and 1 child. And show me the coordinate of the first result."


def get_reference():
 

    node= [{"mcp": "airbnb", "id": "q1", "tool": "airbnb_search", "args": {"location": "Paris","adults": 1, "children": 1,"ignoreRobotsText": True}}]
    res= asyncio.run(get_node_res(node))['q1']
    data = json.loads(res)
    coordinate=data['searchResults'][0]['demandStayListing']['location']['coordinate']
    latitude = coordinate['latitude']
    longitude = coordinate['longitude']

    reference = f"The coordinate of the first Airbnb listing in Paris for 1 adults and 1 child is: Latitude: {latitude}, Longitude: {longitude}."
    return reference
