from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class ToolParamType(str, Enum):
  """工具参数类型枚举类"""

  STRING = 'string'
  NUMBER = 'number'
  BOOLEAN = 'boolean'
  SELECT = 'select'


class ToolParam(BaseModel):
  """工具参数类型"""

  # 参数的实际名字
  name: str
  # 参数展示标题
  label: str
  # 参数类型
  type: ToolParamType
  # 是否必填
  required: bool = False
  # 默认值
  default: Optional[Any] = None
  # 最小值
  min: Optional[float] = None
  # 最大值
  max: Optional[float] = None
  # 下拉菜单选项列表
  options: list[dict[str, Any]] = Field(default_factory=list)


class ToolEntity(BaseModel):
  """工具实体类，存储的信息映射的是工具名.yaml中的信息"""

  # 工具名称
  name: str
  # 工具标签
  label: str
  # 工具描述
  description: str
  # 工具的参数信息
  params: list[ToolParam] = Field(default_factory=list)
