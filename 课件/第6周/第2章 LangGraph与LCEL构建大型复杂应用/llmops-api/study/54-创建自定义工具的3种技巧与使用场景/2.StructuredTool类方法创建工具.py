#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/7/8 11:52
@Author  : thezehui@gmail.com
@File    : 2.StructuredTool类方法创建工具.py
"""
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import StructuredTool


class MultiplyInput(BaseModel):
    a: int = Field(description="第一个数字")
    b: int = Field(description="第二个数字")


def multiply(a: int, b: int) -> int:
    """将传递的两个数字相乘"""
    return a * b


async def amultiply(a: int, b: int) -> int:
    """将传递的两个数字相乘"""
    return a * b


calculator = StructuredTool.from_function(
    func=multiply,
    coroutine=amultiply,
    name="multiply_tool",
    description="将传递的两个数字相乘",
    return_direct=True,
    args_schema=MultiplyInput,
)

# 打印下该工具的相关信息
print("名称: ", calculator.name)
print("描述: ", calculator.description)
print("参数: ", calculator.args)
print("直接返回: ", calculator.return_direct)

# 调用工具
print(calculator.invoke({"a": 2, "b": 8}))
