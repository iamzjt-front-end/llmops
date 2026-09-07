#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/7/4 13:19
@Author  : thezehui@gmail.com
@File    : 1.检索器组件与可运行时配置.py
"""
import dotenv
import weaviate
from langchain_core.runnables import ConfigurableField
from langchain_openai import OpenAIEmbeddings
from langchain_weaviate import WeaviateVectorStore
from weaviate.auth import AuthApiKey

dotenv.load_dotenv()

# 1.构建向量数据库
db = WeaviateVectorStore(
    client=weaviate.connect_to_wcs(
        cluster_url="https://eftofnujtxqcsa0sn272jw.c0.us-west3.gcp.weaviate.cloud",
        auth_credentials=AuthApiKey("21pzYy0orl2dxH9xCoZG1O2b0euDeKJNEbB0"),
    ),
    index_name="DatasetDemo",
    text_key="text",
    embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
)

# 2.转换检索器
retriever = db.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"k": 10, "score_threshold": 0.5},
).configurable_fields(
    search_type=ConfigurableField(id="db_search_type"),
    search_kwargs=ConfigurableField(id="db_search_kwargs"),
)

# 3.修改运行时配置执行MMR搜索，并返回4条数据
mmr_documents = retriever.with_config(
    configurable={
        "db_search_type": "mmr",
        "db_search_kwargs": {
            "k": 4,
        }
    }
).invoke("关于应用配置的接口有哪些？")
print("相似性搜索: ", mmr_documents)
print("内容长度:", len(mmr_documents))

print(mmr_documents[0].page_content[:20])
print(mmr_documents[1].page_content[:20])
