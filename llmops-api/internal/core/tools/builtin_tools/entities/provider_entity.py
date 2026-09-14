import os
from typing import Any

import yaml
from pydantic import BaseModel, Field

from internal.lib.helper import dynamic_import

from .tool_entity import ToolEntity


class ProviderEntity(BaseModel):
  """服务提供商实体，映射的数据是provider.yaml里的每条记录"""

  # 名字
  name: str
  # 标签，展示前端看的
  label: str
  # 描述
  description: str
  # 图标地址
  icon: str
  # 图标的颜色
  background: str
  # 分类信息
  category: str = ''


class Provider(BaseModel):
  """服务提供商，在该类下，可以获取到该服务提供商的所有工具、描述、图标等多个信息"""

  # 服务提供商的名字
  name: str
  # 服务提供商的顺序
  position: int
  # 服务提供商实体
  provider_entity: ProviderEntity
  # 工具实体映射表
  tool_entity_map: dict[str, ToolEntity] = Field(default_factory=dict)
  # 工具函数映射表
  tool_func_map: dict[str, Any] = Field(default_factory=dict)

  def __init__(self, **kwargs):
    """构造函数，完成对应服务提供商的初始化"""
    super().__init__(**kwargs)
    self._provider_init()

  def get_tool(self, tool_name: str) -> Any:
    """根据工具名称，获取到该服务提供商下的指定工具"""
    return self.tool_func_map.get(tool_name)

  def get_tool_entity(self, tool_name: str) -> ToolEntity | None:
    """根据工具名称，获取到该服务提供商下的指定工具实体/信息"""
    return self.tool_entity_map.get(tool_name)

  def get_tool_entities(self) -> list[ToolEntity]:
    """获取该服务提供商下的所有工具实体/信息列表"""
    return list(self.tool_entity_map.values())

  def _provider_init(self):
    """服务提供商初始化函数"""
    # 1.获取当前类的路径，计算得到对应服务提供商的路径
    current_path = os.path.abspath(__file__)
    entities_path = os.path.dirname(current_path)
    provider_path = os.path.join(os.path.dirname(entities_path), 'providers', self.name)

    # 2.组装获取positions.yaml数据
    position_yaml_path = os.path.join(provider_path, 'positions.yaml')
    with open(position_yaml_path, encoding='utf-8') as f:
      position_yaml_data = yaml.safe_load(f)

    # 3.循环读取位置信息获取服务提供商的工具名字
    for tool_name in position_yaml_data:
      # 4.获取工具的yaml数据
      tool_yaml_path = os.path.join(provider_path, f'{tool_name}.yaml')
      with open(tool_yaml_path, encoding='utf-8') as f:
        tool_yaml_data = yaml.safe_load(f)

      # 5.将工具信息实体填充到tool_entity_map中
      self.tool_entity_map[tool_name] = ToolEntity(**tool_yaml_data)

      # 6.动态导入对应的工具，并填充到tool_func_map中
      self.tool_func_map[tool_name] = dynamic_import(
        f'internal.core.tools.builtin_tools.providers.{self.name}', tool_name
      )
