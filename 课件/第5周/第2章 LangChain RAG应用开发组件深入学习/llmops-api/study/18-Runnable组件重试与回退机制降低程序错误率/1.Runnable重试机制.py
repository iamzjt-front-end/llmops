#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/6/6 9:59
@Author  : thezehui@gmail.com
@File    : 1.Runnable重试机制.py
"""
from langchain_core.runnables import RunnableLambda

counter = -1


def func(x):
    global counter
    counter += 1
    print(f"当前的值为 {counter=}")
    return x / counter


chain = RunnableLambda(func).with_retry(stop_after_attempt=2)

resp = chain.invoke(2)

print(resp)
