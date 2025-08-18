import json
import pandas as pd
import asyncio
from .utils import get_node_res  # 假设这是一个可用的异步函数

import re
from datetime import datetime, timedelta

# 问题描述和辅助函数保持不变
question = 'What is the train number with the shortest travel time from Shenzhenbei(深圳北) to Nanning(南宁) on the day after tomorrow, and how long does it take?'

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
    # 将输入的日期字符串转换为 datetime 对象
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    # 增加指定天数
    next_day = date_obj + timedelta(days=add_day)
    # 将结果转换回字符串格式
    return next_day.strftime('%Y-%m-%d')

# 1. 创建一个新的 async 函数来包含所有异步逻辑
async def _get_reference_async():
    """
    在一个事件循环中，按顺序执行所有异步网络请求和数据处理。
    """
    # 获取当前日期
    get_time_node = [{"mcp": "12306-mcp", "id": "q1", "tool": "get-current-date", "args": {}}]
    get_time_res = (await get_node_res(get_time_node))['q1']

    # 根据获取的日期计算出“后天”的日期，并查询车票
    # 注意: 这里的 add_day 参数是 2，因为问题是“后天”
    the_day_after_tomorrow = add_days(get_time_res, 2)
    get_tickets_node = [{"mcp": "12306-mcp", "id": "q2", "tool": "get-tickets", "args": {"date": the_day_after_tomorrow, "fromStation": "IOQ", "toStation": "NNZ"}}]
    get_tickets_res = (await get_node_res(get_tickets_node))['q2']

    # 处理和格式化最终结果的逻辑
    try:
        result = shortest_trip(get_tickets_res)
        if result is None:
            raise TypeError("No trip information found in the response.")
            
        train_no, dur = result
        hours = dur.seconds // 3600
        minutes = (dur.seconds % 3600) // 60  
        cost_time = f"{hours}h {minutes}min"
        find = True
    except (TypeError, AttributeError): # 捕获因找不到车次信息或返回格式不正确导致的错误
        train_no = None
        cost_time = None
        find = False

    if find:
        reference = f"On the day after tomorrow, the train number with the shortest travel time from Shenzhenbei(深圳北) to Nanning(南宁) is {train_no}, and it takes {cost_time}."
    else:
        reference = f"On the day after tomorrow, there is no train from Shenzhenbei(深圳北) to Nanning(南宁)."

    return reference

# 2. 修改你原来的 get_reference 函数，让它只负责启动异步流程
def get_reference():
    """
    同步入口函数，通过调用 asyncio.run() 来启动并等待整个异步流程完成。
    """
    # 只调用一次 asyncio.run()
    return asyncio.run(_get_reference_async())