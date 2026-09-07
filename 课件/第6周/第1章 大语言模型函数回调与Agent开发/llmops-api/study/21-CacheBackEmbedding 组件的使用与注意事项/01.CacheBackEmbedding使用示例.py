#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/6/25 13:36
@Author  : thezehui@gmail.com
@File    : 01.CacheBackEmbedding使用示例.py
"""
import dotenv
import numpy as np
from langchain.embeddings import CacheBackedEmbeddings
from langchain.storage import LocalFileStore
from langchain_openai import OpenAIEmbeddings
from numpy.linalg import norm

dotenv.load_dotenv()


def cosine_similarity(vector1: list, vector2: list) -> float:
    """计算传入两个向量的余弦相似度"""
    # 1.计算内积/点积
    dot_product = np.dot(vector1, vector2)

    # 2.计算向量的范数/长度
    norm_vec1 = norm(vector1)
    norm_vec2 = norm(vector2)

    # 3.计算余弦相似度
    return dot_product / (norm_vec1 * norm_vec2)


embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
embeddings_with_cache = CacheBackedEmbeddings.from_bytes_store(
    embeddings,
    LocalFileStore("./cache/"),
    namespace=embeddings.model,
    query_embedding_cache=True,
)

query_vector = embeddings_with_cache.embed_query("你好，我是慕小课，我喜欢打篮球")
documents_vector = embeddings_with_cache.embed_documents([
    "你好，我是慕小课，我喜欢打篮球",
    "这个喜欢打篮球的人叫慕小课",
    "求知若渴，虚心若愚"
])

print(query_vector)
print(len(query_vector))

print("============")

print(len(documents_vector))
print("vector1与vector2的余弦相似度:", cosine_similarity(documents_vector[0], documents_vector[1]))
print("vector2与vector3的余弦相似度:", cosine_similarity(documents_vector[0], documents_vector[2]))
