
import json
import pandas as pd
import asyncio
from .utils import get_node_res  


import re
from datetime import datetime, timedelta

question = "According to the information on Paper with Code, whose latest published paper has a more recent release date: Chenyuan Wu or Numaan Naeem?"

def get_reference():
   author_name_1 = "Chenyuan Wu"
   author_name_2 = "Numaan Naeem"
   node_1 = [{"mcp": "mcp-paperswithcode", "id": "q1", "tool": "list_papers_by_author_name", "args": {"author_name": author_name_1,"page": 1,"items_per_page": 20}}]
   res_1= asyncio.run(get_node_res(node_1))['q1']
   info_1=json.loads(res_1)['results'][0]
   title_1 = info_1['title']
   published_date_1 = info_1['published']

   node_2 = [{"mcp": "mcp-paperswithcode", "id": "q2", "tool": "list_papers_by_author_name", "args": {"author_name":  author_name_2,"page": 1,"items_per_page": 20}}]
   res_2= asyncio.run(get_node_res(node_2))['q2']
   info_2=json.loads(res_2)['results'][0]
   title_2 = info_2['title']
   published_date_2 = info_2['published']
    
   # Convert published dates to datetime objects for comparison
   date_format = "%Y-%m-%d"
   published_date_1 = datetime.strptime(published_date_1, date_format)
   published_date_2 = datetime.strptime(published_date_2, date_format)
   # Compare the published dates
   if published_date_1 > published_date_2:
      reference = f"{author_name_1}'s latest paper '{title_1}' was published on {published_date_1.strftime(date_format)}, which is more recent than {author_name_2}'s paper '{title_2}' published on {published_date_2.strftime(date_format)}." 
   elif published_date_1 < published_date_2:
      reference = f"{author_name_2}'s latest paper '{title_2}' was published on {published_date_2.strftime(date_format)}, which is more recent than {author_name_1}'s paper '{title_1}' published on {published_date_1.strftime(date_format)}."
   else:
      reference = f"Both {author_name_1}'s latest paper '{title_1}' and {author_name_2}'s latest paper '{title_2}' were published on the same date: {published_date_1.strftime(date_format)}."
   return reference
