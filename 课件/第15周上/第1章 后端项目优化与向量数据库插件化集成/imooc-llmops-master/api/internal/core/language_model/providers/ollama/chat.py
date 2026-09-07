#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/12/01 1:44
@Author  : thezehui@gmail.com
@File    : chat.py
"""
from langchain_ollama import ChatOllama

from internal.core.language_model.entities.model_entity import BaseLanguageModel


class Chat(ChatOllama, BaseLanguageModel):
    """Ollama聊天模型"""
    pass
