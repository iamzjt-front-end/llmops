#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/6/4 15:22
@Author  : thezehui@gmail.com
@File    : 2.configurable_fields替换提示词.py
"""
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import ConfigurableField

# 1.创建提示模板并配置支持动态配置的字段
prompt = PromptTemplate.from_template("请写一篇关于{subject}主题的冷笑话").configurable_fields(
    template_demo=ConfigurableField(id="prompt_template"),
)

# 2.传递配置更改prompt_template并调用生成内容
content = prompt.invoke(
    {"subject": "程序员"},
    config={"configurable": {"prompt_template": "请写一篇关于{subject}主题的藏头诗"}}
).to_string()
print(content)
