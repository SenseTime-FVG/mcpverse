
import json
import pandas as pd
import asyncio
from .utils import get_node_res  


import re
from datetime import datetime, timedelta

question = "According to the information on Paper with Code, whose latest published paper has a more recent release date: Kaiming He or Numaan Naeem?"

def find_latest_paper(papers):
    latest_date = papers[0]['published']
    latest_paper =  papers[0]
    for paper in papers:
        published_date = paper['published']
        if published_date > latest_date:
            latest_date = published_date
            latest_paper = paper
    return latest_paper

def get_reference():
    
    node_1 = [{"mcp": "mcp-paperswithcode", "id": "q1", "tool": "list_papers_by_author_name", "args": {"author_name": "Kaiming He","page": 1,"items_per_page": 20}}]
    res_1= asyncio.run(get_node_res(node_1))['q1']
    info_1=find_latest_paper(json.loads(res_1)['results'])
    title_1 = info_1['title']
    published_date_1 = info_1['published']

    node_2 = [{"mcp": "mcp-paperswithcode", "id": "q2", "tool": "list_papers_by_author_name", "args": {"author_name": "Numaan Naeem","page": 1,"items_per_page": 20}}]
    res_2= asyncio.run(get_node_res(node_2))['q2']
    info_2=find_latest_paper(json.loads(res_2)['results'])
    title_2 = info_2['title']
    published_date_2 = info_2['published']
    
    # Convert published dates to datetime objects for comparison
    date_format = "%Y-%m-%d"
    published_date_1 = datetime.strptime(published_date_1, date_format)
    published_date_2 = datetime.strptime(published_date_2, date_format)
    # Compare the published dates
    if published_date_1 > published_date_2:
       reference = f"Kaiming He's latest paper '{title_1}' was published on {published_date_1.strftime(date_format)}, which is more recent than Numaan Naeem's paper '{title_2}' published on {published_date_2.strftime(date_format)}."
    elif published_date_1 < published_date_2:
       reference = f"Numaan Naeem's latest paper '{title_2}' was published on {published_date_2.strftime(date_format)}, which is more recent than Kaiming He's paper '{title_1}' published on {published_date_1.strftime(date_format)}."
    else:
         reference = f"Both Kaiming He's latest paper '{title_1}' and Numaan Naeem's latest paper '{title_2}' were published on the same date: {published_date_1.strftime(date_format)}."
    return reference
