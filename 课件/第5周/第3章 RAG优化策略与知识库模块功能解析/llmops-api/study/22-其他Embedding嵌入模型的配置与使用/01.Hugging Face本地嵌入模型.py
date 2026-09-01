#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/6/26 14:51
@Author  : thezehui@gmail.com
@File    : 01.Hugging Face本地嵌入模型.py
"""
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L12-v2",
    cache_folder="./embeddings/"
)

query_vector = embeddings.embed_query("你好，我是慕小课，我喜欢打篮球游泳")

print(query_vector)
print(len(query_vector))
