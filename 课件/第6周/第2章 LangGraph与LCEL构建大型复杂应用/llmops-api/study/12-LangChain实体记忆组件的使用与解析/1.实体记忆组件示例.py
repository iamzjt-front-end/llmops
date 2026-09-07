#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/5/23 15:32
@Author  : thezehui@gmail.com
@File    : 1.实体记忆组件示例.py
"""
import dotenv
from langchain.chains.conversation.base import ConversationChain
from langchain.memory import ConversationEntityMemory
from langchain.memory.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE
from langchain_community.chat_models.baidu_qianfan_endpoint import QianfanChatEndpoint

dotenv.load_dotenv()

# llm = ChatOpenAI(model="gpt-4o", temperature=0)
llm = QianfanChatEndpoint()

chain = ConversationChain(
    llm=llm,
    prompt=ENTITY_MEMORY_CONVERSATION_TEMPLATE,
    memory=ConversationEntityMemory(llm=llm),
)

print(chain.invoke({"input": "你好，我是慕小课。我最近正在学习LangChain。"}))
print(chain.invoke({"input": "我最喜欢的编程语言是 Python。"}))
print(chain.invoke({"input": "我住在广州"}))

# 查询实体中的对话
res = chain.memory.entity_store.store
print(res)
