#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/7/8 11:08
@Author  : thezehui@gmail.com
@File    : 1.DuckDuckGo搜索.py
"""
from langchain_community.tools import DuckDuckGoSearchRun

search = DuckDuckGoSearchRun(description="xxx")

print(search.invoke("LangChain的最新版本是什么?"))
print("名字：", search.name)
print("描述：", search.description)
print("参数：", search.args)
print("是否直接返回：", search.return_direct)
# print(convert_to_openai_tool(search))
