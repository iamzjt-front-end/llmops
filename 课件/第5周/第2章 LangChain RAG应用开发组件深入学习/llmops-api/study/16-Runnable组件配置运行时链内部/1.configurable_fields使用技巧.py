#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/6/4 15:05
@Author  : thezehui@gmail.com
@File    : 1.configurable_fields使用技巧.py
"""
import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import ConfigurableField
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

# 1.创建提示模板
prompt = PromptTemplate.from_template("请生成一个小于{x}的随机整数")

# 2.创建LLM大语言模型，并配置temperature参数为可在运行时配置，配置键位llm_temperature
llm = ChatOpenAI(model="gpt-3.5-turbo-16k").configurable_fields(
    temperature=ConfigurableField(
        id="llm_temperature",
        name="大语言模型的温度",
        description="温度越低，大语言模型生成的内容越确定，温度越高，生成内容越随机"
    )
)

# 3.构建链应用
chain = prompt | llm | StrOutputParser()

# 4.正常调用内容
content = chain.invoke({"x": 1000})
print(content)

print("===========================")

# 5.将temperature修改为0调用内容
with_config_chain = chain.with_config(configurable={"llm_temperature": 0})
content = with_config_chain.invoke({"x": 1000})
# content = chain.invoke(
#     {"x": 1000},
#     config={"configurable": {"llm_temperature": 0}}
# )
print(content)
