#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/6/26 15:53
@Author  : thezehui@gmail.com
@File    : 03.百度千帆文本嵌入模型.py
"""
import dotenv
from langchain_community.embeddings.baidu_qianfan_endpoint import QianfanEmbeddingsEndpoint

dotenv.load_dotenv()

embeddings = QianfanEmbeddingsEndpoint()

query_vector = embeddings.embed_query("我叫慕小课，我喜欢打篮球游泳")

print(query_vector)
print(len(query_vector))
