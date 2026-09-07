#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/5/22 23:53
@Author  : thezehui@gmail.com
@File    : 1.BaseChatMemory运行流程解析.py
"""
from langchain.memory.chat_memory import BaseChatMemory

memory = BaseChatMemory(
    input_key="query",
    output_key="output",
    return_messages=True,
    # chat_history 假设
)

memory_variable = memory.load_memory_variables({})

# content = chain.invoke({"query": "你好，我是慕小课你是谁", "chat_history": memory_variable.get("chat_history")})
# memory.save_context({"query": "你好，我是慕小课你是谁"}, {"output": "你好，我是ChatGPT,有什么可以帮到您的"})
memory_variable = memory.load_memory_variables({})
# content = chain.invoke({"query": "你好，我是慕小课你是谁", "chat_history": memory_variable.get("chat_history")})
