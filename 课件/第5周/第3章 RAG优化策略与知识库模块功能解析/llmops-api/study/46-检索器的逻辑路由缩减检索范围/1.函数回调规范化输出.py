#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/7/5 13:08
@Author  : thezehui@gmail.com
@File    : 1.函数回调规范化输出.py
"""
from typing import Literal

import dotenv
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()


class RouteQuery(BaseModel):
    """将用户查询映射到对应的数据源上"""
    datasource: Literal["python_docs", "js_docs", "golang_docs"] = Field(
        description="根据用户的问题，选择哪个数据源最相关以回答用户的问题"
    )


# 1.创建绑定结构化输出的大语言模型
llm = ChatOpenAI(model="gpt-3.5-turbo-16k", temperature=0)
structured_llm = llm.with_structured_output(RouteQuery)

# 2.构建一个问题
question = """为什么下面的代码不工作了，请帮我检查下：

var a = "123"
"""
res: RouteQuery = structured_llm.invoke(question)

print(res)
print(type(res))
print(res.datasource)
