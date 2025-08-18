import json
import pandas as pd
import asyncio
from .utils import get_node_res  # 假设这是一个可用的异步函数

import re
from datetime import datetime, timedelta

question = 'What are the wind directions in Chongqing and Chengdu during the daytime tomorrow according to Amap? Are they the same?'

# 1. 创建一个新的 async 函数来包含所有异步逻辑和后续处理
async def _get_reference_async():
    """
    在一个事件循环中，并行获取两个城市的天气信息，然后比较并生成结果。
    """
    city1 = "成都"
    city2 = "重庆"
    city1_en = "Chengdu"
    city2_en = "Chongqing"
    
    # 中文到英文风向的映射字典
    cn_en_directions = {
        "东": "East", "西": "West", "南": "South", "北": "North",
        "东北": "Northeast", "西北": "Northwest", "东南": "Southeast", "西南": "Southwest",
        "无风向": "No wind" # 增加一个可能的健壮性选项
    }
    
    # 定义两个城市的请求节点
    chengdu_weather_node = [{"mcp": "amap-maps", "id": "q1", "tool": "maps_weather", "args": {"city": city1}}]
    chongqing_weather_node = [{"mcp": "amap-maps", "id": "q2", "tool": "maps_weather", "args": {"city": city2}}]

    try:
        # 2. 使用 asyncio.gather 并行执行两个独立的异步任务
        results = await asyncio.gather(
            get_node_res(chengdu_weather_node),
            get_node_res(chongqing_weather_node)
        )
        
        # 从结果中解析两个城市的风向
        # "forecasts"[1] 代表明天的预报
        chengdu_response_str = results[0]['q1']
        chongqing_response_str = results[1]['q2']
        
        d1_cn = json.loads(chengdu_response_str)["forecasts"][1]["daywind"]
        d2_cn = json.loads(chongqing_response_str)["forecasts"][1]["daywind"]

        # 安全地获取英文翻译，如果找不到则使用中文原文
        d1_en = cn_en_directions.get(d1_cn, d1_cn)
        d2_en = cn_en_directions.get(d2_cn, d2_cn)

    except (KeyError, IndexError, json.JSONDecodeError, asyncio.TimeoutError) as e:
        # 添加健壮的错误处理
        print(f"获取或解析天气数据时出错: {e}")
        return "Sorry, I couldn't retrieve the weather information at the moment."

    # 3. 比较风向并生成最终的答复字符串
    if d1_cn == d2_cn:
        reference = f"Tomorrow, the daytime wind direction in {city1_en} and {city2_en} will be the same: {d1_en}."
    else:
        reference = f"Tomorrow, the daytime wind direction in {city1_en} will be {d1_en}, while in {city2_en} it will be {d2_en}. Thus, they are not the same."

    return reference

# 4. 修改你原来的 get_reference 函数，让它只负责启动异步流程
def get_reference():
    """
    同步入口，调用并运行整个异步天气查询流程。
    """
    # 依然是只调用一次 asyncio.run()
    return asyncio.run(_get_reference_async())