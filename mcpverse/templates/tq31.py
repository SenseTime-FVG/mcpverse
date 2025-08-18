
import json
import pandas as pd
import asyncio
from .utils import get_node_res  


import re
from datetime import datetime, timedelta

question = "Could you please tell me the scheduled departure time, arrival time, and flight number of the earliest flight from Beijing Capital International Airport to Wuhan Tianhe International Airport tomorrow?"

def add_days(date_str: str,add_day=1) -> str:
    # 将输入的日期字符串转换为 datetime 对象
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    
    # 增加一天
    next_day = date_obj + timedelta(days=add_day)
    
    # 将结果转换回字符串格式
    return next_day.strftime('%Y-%m-%d')



def find_earliest_flight(flights,city1,city2):
    earliest_flight = None
    earliest_time = None
   
    for flight in flights:
        deptime = flight['FlightDeptimePlanDate']
        deptime = datetime.strptime(deptime, '%Y-%m-%d %H:%M:%S')  # 得到 datetime 对象
        depcode= flight['FlightDepcode']
        arrcode= flight['FlightArrcode']
        if earliest_time is None or deptime < earliest_time and depcode == city1 and arrcode == city2:
            earliest_time = deptime
            earliest_flight = flight
            
    return earliest_flight

def get_reference():
    city1="PEK"
    city2="WUH"
    get_time_node = [{"mcp": "variflight", "id": "q1", "tool": "getTodayDate", "args": {"random_string": "dummy"}}]
    get_time_res= asyncio.run(get_node_res(get_time_node))['q1']
    
    get_flights_node = [{"mcp": "variflight", "id": "q2", "tool": "searchFlightsByDepArr", "args": {"dep": city1,"arr": city2,"date": add_days(get_time_res,1),"flight_type": "all","flight_no": ""}}]
    get_flights_res= asyncio.run(get_node_res(get_flights_node))['q2']
    data = json.loads(get_flights_res)['data']
    earliest_flight = find_earliest_flight(data, city1, city2)

    flight_no = earliest_flight['FlightNo']
    deptime = earliest_flight['FlightDeptimePlanDate']
    arrtime = earliest_flight['FlightArrtimePlanDate']
    reference = f"Tomorrow, the earliest flight from Beijing Capital International Airport to Wuhan Tianhe International Airport is flight {flight_no}, scheduled to depart at {deptime} and arrive at {arrtime}."
    return reference
