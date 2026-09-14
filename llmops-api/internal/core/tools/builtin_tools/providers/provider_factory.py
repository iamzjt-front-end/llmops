import os
from typing import Any

import yaml
from injector import inject, singleton

from internal.core.tools.builtin_tools.entities import Provider, ProviderEntity


@inject
@singleton
class ProviderFactory:
  """服务提供商工厂类"""

  provider_map: dict[str, Provider] = {}

  def __init__(self):
    """构造函数，初始化对应的provider_tool_map"""
    self._get_provider_tools_map()

  def get_provider(self, provider_name: str) -> Provider:
    """根据传递的名字获取服务提供商"""
    return self.provider_map.get(provider_name)

  def get_providers(self) -> list[Provider]:
    """获取所有服务提供商列表"""
    return list(self.provider_map.values())

  def get_provider_entities(self) -> list[ProviderEntity]:
    """获取所有服务提供商列表实体信息"""
    return [provider.provider_entity for provider in self.provider_map.values()]

  def get_tool(self, provider_name: str, tool_name: str) -> Any:
    """根据服务提供商名字＋工具名字，获取对应实体"""
    provider = self.get_provider(provider_name)
    if provider is None:
      return None
    return provider.get_tool(tool_name)

  def _get_provider_tools_map(self):
    """项目初始化的时候，获取服务提供商、工具的映射关系，并填充provider_tool_map"""
    # 1.检测provider_tool_map是否不为空
    if self.provider_map:
      return

    # 2.获取当前文件/类所在的文件夹路径
    current_path: str = os.path.abspath(__file__)
    providers_path = os.path.dirname(current_path)
    providers_yaml_path = os.path.join(providers_path, 'providers.yaml')

    # 3.读取providers.yaml的数据
    with open(providers_yaml_path, encoding='utf-8') as f:
      providers_yaml_data = yaml.safe_load(f)

    # 4.循环遍历providers.yaml的数据
    for idx, provider_data in enumerate(providers_yaml_data):
      provider_entity = ProviderEntity(**provider_data)
      self.provider_map[provider_entity.name] = Provider(
        name=provider_entity.name,
        position=idx + 1,
        provider_entity=provider_entity,
      )
