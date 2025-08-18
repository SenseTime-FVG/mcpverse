
import json
import pandas as pd
import asyncio
from .utils import get_node_res  


import re
from datetime import datetime, timedelta

question = "Based on info of paper with code, what is the title of Xiaogang Wang's last paper posted on arXiv?"


def find_latest_paper(papers):
    latest_date = papers[0]['published']
    latest_paper=papers[0]
    for paper in papers:
        published_date = paper['published']
        if published_date > latest_date:
            latest_date = published_date
            latest_paper = paper
    return latest_paper
def get_reference():
    
    node_1 = [{"mcp": "mcp-paperswithcode", "id": "q1", "tool": "list_papers_by_author_name", "args": {"author_name": "Xiaogang Wang","page": 1,"items_per_page": 20}}]
    
    res_1= asyncio.run(get_node_res(node_1))['q1']
    info=find_latest_paper(json.loads(res_1)['results'])
    title = info['title']
    published_date = info['published']
    reference= f"The title of Xiaogang Wang's last paper posted on arXiv is '{title}', published on {published_date}."
    return reference
