
import json
import pandas as pd
import asyncio
from .utils import get_node_res  


import re
from datetime import datetime, timedelta

question = "Search for Airbnb listings in Hong Kong for 3 adults and 1 child. And show me the rating condition of the first result."


def get_reference():
 

    node= [{"mcp": "airbnb", "id": "q1", "tool": "airbnb_search", "args": {"location": "Hong Kong","adults": 3, "children": 1,"ignoreRobotsText": True}}]
    res= asyncio.run(get_node_res(node))['q1']
    data = json.loads(res)
    rating_condition=data['searchResults'][0]['avgRatingA11yLabel']
    reference = f"The rating condition of the first Airbnb listing in Hong Kong for 3 adults and 1 child is: {rating_condition}."
    return reference
