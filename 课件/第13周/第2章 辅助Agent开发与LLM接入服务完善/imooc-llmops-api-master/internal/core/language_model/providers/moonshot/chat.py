#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/12/01 20:33
@Author  : thezehui@gmail.com
@File    : chat.py
"""
from langchain_community.chat_models.moonshot import MoonshotChat

from internal.core.language_model.entities.model_entity import BaseLanguageModel


class Chat(MoonshotChat, BaseLanguageModel):
    """月之暗面聊天模型"""
    pass
