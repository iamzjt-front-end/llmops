#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/7/1 23:30
@Author  : thezehui@gmail.com
@File    : 4.通用文件加载器.py
"""
from langchain_community.document_loaders import UnstructuredFileLoader

loader = UnstructuredFileLoader("./项目API资料.md")
documents = loader.load()

print(documents)
print(len(documents))
print(documents[0].metadata)
