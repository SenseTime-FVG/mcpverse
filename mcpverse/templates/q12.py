
import json
import pandas as pd
import asyncio
from .utils import get_node_res  


import re
from datetime import datetime, timedelta

question = "Which has more five-star reviews in the US App Store, the one with ID 570060128 or the one with ID 553834731?"



def get_reference():
 
    ID1= 570060128
    ID2= 553834731
    node_1= [{"mcp": "appinsightmcp", "id": "q1", "tool": "app-store-ratings", "args": {"id": ID1, "country": "us"}},]
    res_1= asyncio.run(get_node_res(node_1))['q1']
    data_1 = json.loads(res_1)
    count_1 = data_1['histogram']['5']

    node_2= [{"mcp": "appinsightmcp", "id": "q2", "tool": "app-store-ratings", "args": {"id": ID2, "country": "us"}},]
    res_2= asyncio.run(get_node_res(node_2))['q2']
    data_2 = json.loads(res_2)
    count_2 = data_2['histogram']['5']
    if count_1 > count_2:
        reference = f"The app with ID {ID1} has more five-star reviews ({count_1}) than the app with ID {ID2} ({count_2})."
    elif count_1 < count_2:
        reference = f"The app with ID {ID2} has more five-star reviews ({count_2}) than the app with ID {ID1} ({count_1})."
    else:
        reference = f"Both apps have the same number of five-star reviews: {count_1}."

    return reference
