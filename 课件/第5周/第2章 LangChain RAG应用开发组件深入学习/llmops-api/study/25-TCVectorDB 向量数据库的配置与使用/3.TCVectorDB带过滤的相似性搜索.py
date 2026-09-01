#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/6/29 16:30
@Author  : thezehui@gmail.com
@File    : 3.TCVectorDB带过滤的相似性搜索.py
"""
import os

import dotenv
from langchain_community.vectorstores import TencentVectorDB
from langchain_community.vectorstores.tencentvectordb import (
    ConnectionParams,
    MetaField,
    META_FIELD_TYPE_UINT64,
)
from langchain_openai import OpenAIEmbeddings

dotenv.load_dotenv()

embedding = OpenAIEmbeddings(model="text-embedding-3-small")
db = TencentVectorDB(
    embedding=None,
    connection_params=ConnectionParams(
        url=os.environ.get("TC_VECTOR_DB_URL"),
        username=os.environ.get("TC_VECTOR_DB_USERNAME"),
        key=os.environ.get("TC_VECTOR_DB_KEY"),
        timeout=int(os.environ.get("TC_VECTOR_DB_TIMEOUT")),
    ),
    database_name=os.environ.get("TC_VECTOR_DB_DATABASE"),
    collection_name="dataset-filter",
    meta_fields=[
        MetaField(name="page", data_type=META_FIELD_TYPE_UINT64),
    ]
)

texts = [
    "笨笨是一只很喜欢睡觉的猫咪",
    "我喜欢在夜晚听音乐，这让我感到放松。",
    "猫咪在窗台上打盹，看起来非常可爱。",
    "学习新技能是每个人都应该追求的目标。",
    "我最喜欢的食物是意大利面，尤其是番茄酱的那种。",
    "昨晚我做了一个奇怪的梦，梦见自己在太空飞行。",
    "我的手机突然关机了，让我有些焦虑。",
    "阅读是我每天都会做的事情，我觉得很充实。",
    "他们一起计划了一次周末的野餐，希望天气能好。",
    "我的狗喜欢追逐球，看起来非常开心。",
]
metadatas = [
    {"page": 1},
    {"page": 2},
    {"page": 3},
    {"page": 4},
    {"page": 5},
    {"page": 6, "account_id": 1},
    {"page": 7},
    {"page": 8},
    {"page": 9},
    {"page": 10},
]

ids = db.add_texts(texts, metadatas)
print("添加文档id列表:", ids)

print(db.similarity_search_with_score("我养了一只猫，叫笨笨", expr="page>=9"))
