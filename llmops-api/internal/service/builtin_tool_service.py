from dataclasses import dataclass

from injector import inject
from pydantic import BaseModel

from internal.core.tools.builtin_tools.providers import BuiltinProviderManager
from internal.exception import NotFoundException


@inject
@dataclass
class BuiltinToolService:
  """内置工具服务"""

  builtin_provider_manager: BuiltinProviderManager

  def get_builtin_tools(self) -> list:
    """获取LLMOps所有内置提供商＋工具信息"""
    # 1.获取所有的提供商
    providers = self.builtin_provider_manager.get_providers()

    # 2.遍历所有的提供商并提取工具信息
    builtin_tools = []
    for provider in providers:
      provider_entity = provider.provider_entity
      builtin_tool = {
        **provider_entity.model_dump(exclude={'icon'}),
        'tools': [],
      }

      # 3.循环遍历提取服务商的所有工具实体
      for tool_entities in provider.get_tool_entities():
        # 4.构建工具实体信息
        tool = provider.get_tool(tool_entities.name)

        # 5.构建工具实体信息
        tool_dict = {
          **tool_entities.model_dump(),
          'input': self.get_tool_input(tool),
        }
        builtin_tool['tools'].append(tool_dict)

      builtin_tools.append(builtin_tool)

    return builtin_tools

  def get_provider_tool(self, provider_name: str, tool_name: str) -> dict:
    """根据传递的提供商名字＋工具名字，获取指定的工具信息"""
    # 1.获取内置的提供商
    provider = self.builtin_provider_manager.get_provider(provider_name)
    if provider is None:
      raise NotFoundException(f'该提供商{provider_name}不存在')

    # 2.获取该提供商下对应的工具实体
    tool_entity = provider.get_tool_entity(tool_name)
    if tool_entity is None:
      raise NotFoundException(f'该工具{tool_name}不存在')

    # 3.获取工具函数并提取input参数信息
    tool = provider.get_tool(tool_name)

    # 4.组装提供商和工具实体信息
    provider_entity = provider.provider_entity
    builtin_tool = {
      'provider': {**provider_entity.model_dump(exclude={'icon'})},
      **tool_entity.model_dump(),
      'input': self.get_tool_input(tool),
    }
    return builtin_tool

  @classmethod
  def get_tool_input(cls, tool: str) -> list:
    """根据传入的工具获取input信息"""
    inputs = []

    if hasattr(tool, 'args_schema') and issubclass(tool.args_schema, BaseModel):
      for field_name, model_field in tool.args_schema.model_fields.items():
        inputs.append(
          {
            'name': field_name,
            'description': model_field.description or '',
            'required': model_field.is_required(),
            'type': model_field.annotation.__name__,
          }
        )

    return inputs
