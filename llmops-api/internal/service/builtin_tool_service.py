from dataclasses import dataclass

from injector import inject
from pydantic import BaseModel

from internal.core.tools.builtin_tools.providers import BuiltinProviderManager


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
        tool_dict = {
          **tool_entities.model_dump(),
          'input': [],
        }

        # 5.从服务商中获取工具函数
        tool = provider.get_tool(tool_entities.name)

        # 6.检测工具是否有args_schema属性，并且是BaseModel的子类
        if hasattr(tool, 'args_schema') and issubclass(tool.args_schema, BaseModel):
          inputs = []
          for field_name, model_field in tool.args_schema.model_fields.items():
            inputs.append(
              {
                'name': field_name,
                'description': model_field.description or '',
                'required': model_field.is_required(),
                'type': model_field.annotation.__name__,
              }
            )
          tool_dict['input'] = inputs
        builtin_tool['tools'].append(tool_dict)

      builtin_tools.append(builtin_tool)

    return builtin_tools

  def get_provider_tool(self, provider_name: str, tool_name: str) -> dict:
    """根据传递的提供商名字＋工具名字，获取指定的工具信息"""
    pass
