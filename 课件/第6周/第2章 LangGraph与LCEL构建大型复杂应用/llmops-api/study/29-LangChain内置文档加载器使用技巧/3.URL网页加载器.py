#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/7/1 23:17
@Author  : thezehui@gmail.com
@File    : 3.URL网页加载器.py
"""
from langchain_community.document_loaders import WebBaseLoader

loader = WebBaseLoader("https://imooc.com")
documents = loader.load()

print(documents)
print(len(documents))
print(documents[0].metadata)
