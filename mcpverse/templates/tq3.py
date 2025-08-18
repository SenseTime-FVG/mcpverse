import json
import pandas as pd
import asyncio
from .utils import get_node_res  # 假设这是一个可用的异步函数

import re
from datetime import datetime, timedelta

question = 'Which city will have a higher night-time temperature tomorrow, Chengdu or Chongqing, according to Amap(accurate to whole number)? Also show the temperature of both cities.'

# 1. 创建一个新的 async 函数来包含所有异步逻辑
async def _get_reference_async():
    """
    在一个事件循环中，并行获取两个城市的天气信息，然后比较并生成结果。
    """
    city1 = "成都"
    city2 = "重庆"
    city1_en = "Chengdu"
    city2_en = "Chongqing"
    
    # 定义两个城市的请求节点
    # (修正了原始代码中的变量名拼写错误 tiem -> weather)
    chengdu_weather_node = [{"mcp": "amap-maps", "id": "q1", "tool": "maps_weather", "args": {"city": city1}}]
    chongqing_weather_node = [{"mcp": "amap-maps", "id": "q2", "tool": "maps_weather", "args": {"city": city2}}]

    try:
        # 2. 使用 asyncio.gather 来并行执行两个独立的异步任务
        # 这比一个接一个地 await 更高效
        results = await asyncio.gather(
            get_node_res(chengdu_weather_node),
            get_node_res(chongqing_weather_node)
        )
        
        # 从结果中解析两个城市的温度
        # results[0] 对应第一个任务的结果，results[1] 对应第二个
        chengdu_response_str = results[0]['q1']
        chongqing_response_str = results[1]['q2']
        
        # "forecasts"[1] 代表明天的预报 ("forecasts"[0] 是今天)
        w1 = int(json.loads(chengdu_response_str)["forecasts"][1]["nighttemp"])
        w2 = int(json.loads(chongqing_response_str)["forecasts"][1]["nighttemp"])

    except (KeyError, IndexError, json.JSONDecodeError, asyncio.TimeoutError) as e:
        # 添加健壮的错误处理，应对网络问题或返回数据格式不符
        print(f"Error fetching or parsing weather data: {e}")
        return "Sorry, I couldn't retrieve the weather information at the moment."

    # 3. 比较温度并生成最终的答复字符串
    if w1 > w2:
        reference = f"Tomorrow, the night-time temperature in {city1_en} will be higher than that in {city2_en}, with {city1_en} at {w1}°C and {city2_en} at {w2}°C."
    elif w1 < w2:
        reference = f"Tomorrow, the night-time temperature in {city2_en} will be higher than that in {city1_en}, with {city2_en} at {w2}°C and {city1_en} at {w1}°C."
    else: # w1 == w2
        reference = f"Tomorrow, the night-time temperature in {city1_en} and {city2_en} will be the same, both at {w1}°C."

    return reference

# 4. 修改你原来的 get_reference 函数，让它只负责启动异步流程
def get_reference():
    """
    同步入口，调用并运行整个异步天气查询流程。
    """
    # 依然是只调用一次 asyncio.run()
    return asyncio.run(_get_reference_async())