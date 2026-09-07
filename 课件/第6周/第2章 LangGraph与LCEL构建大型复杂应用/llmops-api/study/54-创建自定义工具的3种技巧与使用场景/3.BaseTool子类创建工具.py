#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/7/8 12:25
@Author  : thezehui@gmail.com
@File    : 3.BaseTool子类创建工具.py
"""
from typing import Any, Type

from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool


class MultiplyInput(BaseModel):
    a: int = Field(description="第一个数字")
    b: int = Field(description="第二个数字")


class MultiplyTool(BaseTool):
    """乘法计算工具"""
    name = "multiply_tool"
    description = "将传递的两个数字相乘后返回"
    args_schema: Type[BaseModel] = MultiplyInput

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        """将传入的a和b相乘后返回"""
        return kwargs.get("a") * kwargs.get("b")


calculator = MultiplyTool()

# 打印下该工具的相关信息
print("名称: ", calculator.name)
print("描述: ", calculator.description)
print("参数: ", calculator.args)
print("直接返回: ", calculator.return_direct)

# 调用工具
print(calculator.invoke({"a": 2, "b": 8}))
