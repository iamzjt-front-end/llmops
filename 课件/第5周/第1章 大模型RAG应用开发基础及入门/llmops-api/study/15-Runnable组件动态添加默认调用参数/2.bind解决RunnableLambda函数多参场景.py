#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/6/4 11:48
@Author  : thezehui@gmail.com
@File    : 2.bind解决RunnableLambda函数多参场景.py
"""
import random

from langchain_core.runnables import RunnableLambda


def get_weather(location: str, unit: str, name: str) -> str:
    """根据传入的位置+温度单位获取对应的天气信息"""
    print("location:", location)
    print("unit:", unit)
    print("name:", name)
    return f"{location}天气为{random.randint(24, 40)}{unit}"


get_weather_runnable = RunnableLambda(get_weather).bind(unit="摄氏度", name="慕小课")

resp = get_weather_runnable.invoke("广州")

print(resp)
