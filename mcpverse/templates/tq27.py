
import json
import pandas as pd
import asyncio
from .utils import get_node_res  


import re
from datetime import datetime, timedelta

question = 'What is the train number with the shortest travel time from  Guangzhounan(广州南) to Nanning(南宁) on the day after tomorrow, and how long does it take?'


def shortest_trip(text: str):
    """
    解析车次信息并找出历时最短的车次
    :param text: 包含车次、时间段、历时等信息的原始字符串
    :return: (train_no, duration) 形式的元组，duration 为 datetime.timedelta
    """
    # 正则：车次号在行开头的 G\d+，历时部分形如 历时：hh:mm
    pattern = re.compile(
        r'^([A-Za-z]\d+).*?历时：(\d{2}):(\d{2})',
        re.MULTILINE | re.DOTALL
    )
    
    shortest = None            # (train_no, timedelta)
    for train_no, hh, mm in pattern.findall(text):
        dur = timedelta(hours=int(hh), minutes=int(mm))
        if shortest is None or dur < shortest[1]:
            shortest = (train_no, dur)
    return shortest

def add_days(date_str: str,add_day=1) -> str:
    # 将输入的日期字符串转换为 datetime 对象
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    
    # 增加一天
    next_day = date_obj + timedelta(days=add_day)
    
    # 将结果转换回字符串格式
    return next_day.strftime('%Y-%m-%d')

def get_reference():
    get_time_node = [{"mcp": "12306-mcp", "id": "q1", "tool": "get-current-date", "args": {}}]
    get_time_res= asyncio.run(get_node_res(get_time_node))['q1']


    get_tickets_node = [{"mcp": "12306-mcp", "id": "q2", "tool": "get-tickets", "args": {"date": add_days(get_time_res,2), "fromStation": "IZQ", "toStation": "NNZ"}}]
    get_tickets_res= asyncio.run(get_node_res(get_tickets_node))['q2']


   

    try:
        train_no,dur = shortest_trip(get_tickets_res)
        hours = dur.seconds // 3600
        minutes = (dur.seconds % 3600) // 60  
        cost_time= f"{hours}h {minutes}min"
        find=True
    except:
        train_no = None
        cost_time = None
        find = False

    if find:
        reference = f"On the day after tomorrow, the train number with the shortest travel time from Guangzhounan(广州南) to Nanning(南宁) is {train_no}, and it takes {cost_time}."
    else:
        reference = f"On the day after tomorrow, there is no train from Guangzhounan(广州南) to Nanning(南宁)."
        

    return reference
