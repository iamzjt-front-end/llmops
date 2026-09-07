#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/12/30 17:58
@Author  : thezehui@gmail.com
@File    : 模型.py
"""
import dotenv
from langchain_community.chat_models.tongyi import ChatTongyi

dotenv.load_dotenv()

llm = ChatTongyi(model="qwen-plus")

print(llm.invoke("你好，你是？"))
