import json
import pandas as pd
import asyncio
from .utils import get_node_res
import re
from datetime import datetime, timedelta

# question 和 helper 函数保持不变
question = 'What is the train number with the shortest travel time from Shenzhen North(深圳北) to Liuzhou(柳州) tomorrow, and how long does it take?'

def shortest_trip(text: str):
    """
    解析车次信息并找出历时最短的车次
    :param text: 包含车次、时间段、历时等信息的原始字符串
    :return: (train_no, duration) 形式的元组，duration 为 datetime.timedelta
    """
    pattern = re.compile(
        r'^([A-Za-z]\d+).*?历时：(\d{2}):(\d{2})',
        re.MULTILINE | re.DOTALL
    )
    
    shortest = None
    for train_no, hh, mm in pattern.findall(text):
        dur = timedelta(hours=int(hh), minutes=int(mm))
        if shortest is None or dur < shortest[1]:
            shortest = (train_no, dur)
    return shortest

def add_days(date_str: str, add_day=1) -> str:
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    next_day = date_obj + timedelta(days=add_day)
    return next_day.strftime('%Y-%m-%d')


# 1. 创建一个新的 async 函数来包含所有异步逻辑
async def _get_reference_async():
    # 在同一个事件循环中执行所有 await 操作
    get_time_node = [{"mcp": "12306-mcp", "id": "q1", "tool": "get-current-date", "args": {}}]
    # 使用 await 而不是 asyncio.run
    get_time_res = (await get_node_res(get_time_node))['q1']

    get_tickets_node = [{"mcp": "12306-mcp", "id": "q2", "tool": "get-tickets", "args": {"date": add_days(get_time_res, 1), "fromStation": "IOQ", "toStation": "LZZ"}}]
    # 再次使用 await
    get_tickets_res = (await get_node_res(get_tickets_node))['q2']

    # 处理结果的逻辑保持不变
    try:
        # 建议: 避免使用空的 except，最好捕获更具体的异常，例如 TypeError
        result = shortest_trip(get_tickets_res)
        if result is None:
            raise TypeError("No trip found")
            
        train_no, dur = result
        hours = dur.seconds // 3600
        minutes = (dur.seconds % 3600) // 60  
        cost_time = f"{hours}h {minutes}min"
        find = True
    except (TypeError, AttributeError): # 捕获更具体的异常
        train_no = None
        cost_time = None
        find = False

    if find:
        reference = f"Tomorrow, the train number with the shortest travel time from Shenzhen North(深圳北) to Liuzhou(柳州) is {train_no}, and it takes {cost_time}."
    else:
        reference = f"Tomorrow, there is no train from Shenzhen North(深圳北) to Liuzhou(柳州)."
    return reference

# 2. 修改你原来的 get_reference 函数，让它只负责启动异步流程
def get_reference():
    """
    同步函数的入口，负责调用并运行整个异步流程。
    """
    # 只调用一次 asyncio.run()
    return asyncio.run(_get_reference_async())