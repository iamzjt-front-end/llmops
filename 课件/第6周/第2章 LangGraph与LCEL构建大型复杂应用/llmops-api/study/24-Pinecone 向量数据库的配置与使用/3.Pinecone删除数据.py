#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/7/17 9:18
@Author  : thezehui@gmail.com
@File    : 3.Pinecone删除数据.py
"""
import dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

dotenv.load_dotenv()

embedding = OpenAIEmbeddings(model="text-embedding-3-small")
db = PineconeVectorStore(index_name="llmops", embedding=embedding, namespace="dataset")

id = "23cb7d6f-f77d-4465-8634-9c1ca7f93895"
db.delete([id], namespace="dataset")
# pinecone_index = db.get_pinecone_index("llmops")
# pinecone_index.update(id="xxx", values=[], metadata={}, namespace="xxx")
