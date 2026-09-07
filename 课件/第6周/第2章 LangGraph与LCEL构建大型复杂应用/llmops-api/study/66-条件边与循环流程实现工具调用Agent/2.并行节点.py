#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/7/15 11:42
@Author  : thezehui@gmail.com
@File    : 2.并行节点.py
"""
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph.message import StateGraph, MessagesState

graph_builder = StateGraph(MessagesState)


def chatbot(state: MessagesState, config: dict) -> Any:
    return {"messages": [AIMessage(content="你好，我是OpenAI开发的聊天机器人")]}


def parallel1(state: MessagesState, config: dict) -> Any:
    print("并行1: ", state)
    return {"messages": [HumanMessage(content="这是并行1函数")]}


def parallel2(state: MessagesState, config: dict) -> Any:
    print("并行2: ", state)
    return {"messages": [HumanMessage(content="这是并行2函数")]}


def chat_end(state: MessagesState, config: dict) -> Any:
    print("聊天结束: ", state)
    return {"messages": [HumanMessage(content="这是聊天结束函数")]}


graph_builder.add_node("chat_bot", chatbot)
graph_builder.add_node("parallel1", parallel1)
graph_builder.add_node("parallel2", parallel2)
graph_builder.add_node("chat_end", chat_end)

graph_builder.set_entry_point("chat_bot")
graph_builder.set_finish_point("chat_end")
graph_builder.add_edge("chat_bot", "parallel1")
graph_builder.add_edge("chat_bot", "parallel2")
graph_builder.add_edge("parallel2", "chat_end")

graph = graph_builder.compile()

print(graph.invoke({"messages": [HumanMessage(content="你好，你是")]}))
