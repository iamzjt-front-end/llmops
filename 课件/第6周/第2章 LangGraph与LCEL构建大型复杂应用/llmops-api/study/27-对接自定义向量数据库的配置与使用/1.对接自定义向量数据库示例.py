#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/6/30 8:12
@Author  : thezehui@gmail.com
@File    : 1.对接自定义向量数据库示例.py
"""
import uuid
from typing import List, Optional, Any, Iterable, Type

import dotenv
import numpy as np
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore
from langchain_openai import OpenAIEmbeddings


class MemoryVectorStore(VectorStore):
    """基于内存+欧几里得距离的向量数据库"""
    store: dict = {}  # 存储向量的临时变量

    def __init__(self, embedding: Embeddings):
        self._embedding = embedding

    def add_texts(self, texts: Iterable[str], metadatas: Optional[List[dict]] = None, **kwargs: Any) -> List[str]:
        """将数据添加到向量数据库中"""
        # 1.检测metadata的数据格式
        if metadatas is not None and len(metadatas) != len(texts):
            raise ValueError("metadatas格式错误")

        # 2.将数据转换成文本嵌入/向量和ids
        embeddings = self._embedding.embed_documents(texts)
        ids = [str(uuid.uuid4()) for _ in texts]

        # 3.通过for循环组装数据记录
        for idx, text in enumerate(texts):
            self.store[ids[idx]] = {
                "id": ids[idx],
                "text": text,
                "vector": embeddings[idx],
                "metadata": metadatas[idx] if metadatas is not None else {},
            }

        return ids

    def similarity_search(self, query: str, k: int = 4, **kwargs: Any) -> List[Document]:
        """传入对应的query执行相似性搜索"""
        # 1.将query转换成向量
        embedding = self._embedding.embed_query(query)

        # 2.循环和store中的每一个向量进行比较，计算欧几里得距离
        result = []
        for key, record in self.store.items():
            distance = self._euclidean_distance(embedding, record["vector"])
            result.append({"distance": distance, **record})

        # 3.排序，欧几里得距离越小越靠前
        sorted_result = sorted(result, key=lambda x: x["distance"])

        # 4.取数据，取k条数据
        result_k = sorted_result[:k]

        return [
            Document(page_content=item["text"], metadata={**item["metadata"], "score": item["distance"]})
            for item in result_k
        ]

    @classmethod
    def from_texts(cls: Type["MemoryVectorStore"], texts: List[str], embedding: Embeddings,
                   metadatas: Optional[List[dict]] = None,
                   **kwargs: Any) -> "MemoryVectorStore":
        """从文本和元数据中去构建向量数据库"""
        memory_vector_store = cls(embedding=embedding)
        memory_vector_store.add_texts(texts, metadatas, **kwargs)
        return memory_vector_store

    @classmethod
    def _euclidean_distance(cls, vec1: list, vec2: list) -> float:
        """计算两个向量的欧几里得距离"""
        return np.linalg.norm(np.array(vec1) - np.array(vec2))


dotenv.load_dotenv()

# 1.创建初始数据与嵌入模型
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
embedding = OpenAIEmbeddings(model="text-embedding-3-small")

# 2.构建自定义向量数据库
db = MemoryVectorStore(embedding=embedding)

ids = db.add_texts(texts, metadatas)
print(ids)

# 3.执行检索
print(db.similarity_search("笨笨是谁？"))
