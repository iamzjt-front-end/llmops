#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/7/12 9:51
@Author  : thezehui@gmail.com
@File    : 1.错误捕获.py
"""
from typing import Any

import dotenv
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()


@tool
def complex_tool(int_arg: int, float_arg: float, dict_arg: dict) -> int:
    """使用复杂工具进行复杂计算操作"""
    return int_arg * float_arg


def try_except_tool(tool_args: dict, config: RunnableConfig) -> Any:
    try:
        return complex_tool.invoke(tool_args, config=config)
    except Exception as e:
        return f"调用工具时使用以下参数:\n\n{tool_args}\n\n引发了以下错误:\n\n{type(e)}: {e}"


# 1.创建大语言模型并绑定工具
llm = ChatOpenAI(model="gpt-3.5-turbo-16k", temperature=0)
llm_with_tools = llm.bind_tools([complex_tool])

# 2.创建链并执行工具
chain = llm_with_tools | (lambda msg: msg.tool_calls[0]["args"]) | try_except_tool

# 3.调用链
print(chain.invoke("使用复杂工具，对应参数为5和2.1"))
