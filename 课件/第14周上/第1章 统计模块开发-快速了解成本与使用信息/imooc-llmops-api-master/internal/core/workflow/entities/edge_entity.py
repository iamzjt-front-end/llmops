#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/11/25 17:11
@Author  : thezehui@gmail.com
@File    : edge_entity.py
"""
from uuid import UUID

from langchain_core.pydantic_v1 import BaseModel

from internal.core.workflow.entities.node_entity import NodeType


class BaseEdgeData(BaseModel):
    """基础边数据"""
    id: UUID  # 边记录id
    source: UUID  # 边起点对应的节点id
    source_type: NodeType  # 边起点类型
    target: UUID  # 边目标对应的节点id
    target_type: NodeType  # 边目标类型
