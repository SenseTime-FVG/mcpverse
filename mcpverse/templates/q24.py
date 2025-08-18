# ========= Copyright 2023-2024 @ CAMEL-AI.org. All Rights Reserved. =========
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ========= Copyright 2023-2024 @ CAMEL-AI.org. All Rights Reserved. =========

import asyncio
import json
import re

from .utils import get_node_res

question = "Based on info of aribnb, in Parisian homestays with a check-in date of December 25, 2025, and check-out date of December 30, 2025, accommodating up to 4 adults and priced between 500 and 800, what is the highest total price in dollars?"


def get_highest_price_and_bedrooms(data):
    listings = data['searchResults']
    if not listings:
        return None

    max_price = 0

    for listing in listings:
        price_info = listing['structuredDisplayPrice']['primaryLine'][
            'accessibilityLabel'
        ]
        price = re.search(r'\$([\d,]+)', price_info)[0][1:]
        price = int(price.replace(',', ''))
        if price > max_price:
            max_price = price

    return max_price


def get_reference():
    node = [
        {
            "mcp": "airbnb",
            "id": "q1",
            "tool": "airbnb_search",
            "args": {
                "location": "Paris, France",
                "checkin": "2025-12-25",
                "checkout": "2025-12-30",
                "adults": 4,
                "minPrice": 500,
                "maxPrice": 800,
                "ignoreRobotsText": True,
            },
        }
    ]
    res = asyncio.run(get_node_res(node))['q1']

    data = json.loads(res)
    highest_price = get_highest_price_and_bedrooms(data)
    if highest_price is None:
        reference = "No listings found for the specified criteria."
    else:
        reference = f"The highest total price in dollars for Parisian homestays with the specified criteria is ${highest_price}."

    return reference
