
import json
import pandas as pd
import asyncio
from .utils import get_node_res  


import re
from datetime import datetime, timedelta

question = "What is the tasks included in Chenyuan Wu's latest paper according to the information on Paper with Code?"
def get_reference():
    
    author_name = "Chenyuan Wu"
    node_1 = [{"mcp": "mcp-paperswithcode", "id": "q1", "tool": "list_papers_by_author_name", "args": {"author_name": author_name,"page": 1,"items_per_page": 20}}]
    res_1= asyncio.run(get_node_res(node_1))['q1']
    info_1=json.loads(res_1)['results'][0]
    title_1 = info_1['title']
    
    node_2 = [{"mcp": "mcp-paperswithcode", "id": "q2", "tool": "search_papers", "args": {"title": title_1}}]
    res_2= asyncio.run(get_node_res(node_2))['q2']
    info_2=json.loads(res_2)['results'][0]
    paperID = info_2['id']
    
    node3 = [{"mcp": "mcp-paperswithcode", "id": "q3", "tool": "list_paper_tasks", "args": {"paper_id": paperID}}]
    res_3 = asyncio.run(get_node_res(node3))['q3']
    info = json.loads(res_3)['results']
    tasks = [task['name'] for task in info]

    if not tasks:
        return f"No tasks found for the latest paper {title_1} by {author_name}."
    else:
        return f"The tasks included in {author_name}'s latest paper '{title_1}' are: {', '.join(tasks)}."
