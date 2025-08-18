
import json
import pandas as pd
import asyncio
from .utils import get_node_res  


import re
from datetime import datetime, timedelta

question = "Search for Airbnb listings in London for 1 adults and 2 child. And show me the rating condition of the first result."


def get_reference():
 

    node= [{"mcp": "airbnb", "id": "q1", "tool": "airbnb_search", "args": {"location": "London","adults": 1, "children": 2,"ignoreRobotsText": True}}]
    res= asyncio.run(get_node_res(node))['q1']
    data = json.loads(res)
    rating_condition=data['searchResults'][0]['avgRatingA11yLabel']
    reference = f"The rating condition of the first Airbnb listing in London for 1 adults and 2 child is: {rating_condition}."
    return reference
