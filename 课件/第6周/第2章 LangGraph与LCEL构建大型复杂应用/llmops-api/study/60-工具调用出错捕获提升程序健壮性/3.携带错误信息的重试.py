#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/7/12 10:24
@Author  : thezehui@gmail.com
@File    : 3.携带错误信息的重试.py
"""
from typing import Any

import dotenv
from langchain_core.messages import ToolCall, AIMessage, ToolMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()


class CustomToolException(Exception):
    def __init__(self, tool_call: ToolCall, exception: Exception) -> None:
        super().__init__()
        self.tool_call = tool_call
        self.exception = exception


@tool
def complex_tool(int_arg: int, float_arg: float, dict_arg: dict) -> int:
    """使用复杂工具进行复杂计算操作"""
    return int_arg * float_arg


def tool_custom_exception(msg: AIMessage, config: RunnableConfig) -> Any:
    try:
        return complex_tool.invoke(msg.tool_calls[0]["args"], config=config)
    except Exception as e:
        raise CustomToolException(msg.tool_calls[0], e)


def exception_to_messages(inputs: dict) -> dict:
    # 1.从inputs中分离出异常信息
    exception = inputs.pop("exception")
    # 2.根据异常信息组装占位消息列表
    messages = [
        AIMessage(content="", tool_calls=[exception.tool_call]),
        ToolMessage(tool_call_id=exception.tool_call["id"], content=str(exception.exception)),
        HumanMessage(content="最后一次工具调用引发了异常，请尝试使用更正的参数再次调用该工具，请不要重复犯错"),
    ]
    inputs["last_output"] = messages
    return inputs


# 1.创建prompt
prompt = ChatPromptTemplate.from_messages([
    ("human", "{query}"),
    ("placeholder", "{last_output}")
])

# 2.创建大语言模型并绑定工具
llm = ChatOpenAI(model="gpt-4o", temperature=0).bind_tools(
    tools=[complex_tool], tool_choice="complex_tool",
)

# 3.创建链并执行工具
chain = prompt | llm | tool_custom_exception
self_correcting_chain = chain.with_fallbacks(
    [exception_to_messages | chain], exception_key="exception"
)

# 4.调用自我纠正链完成任务
print(self_correcting_chain.invoke({"query": "使用复杂工具，对应参数为5和2.1"}))
