from dataclasses import dataclass

from injector import inject

from internal.service.builtin_tool_service import BuiltinToolService
from pkg.response import success_json


@inject
@dataclass
class BuiltinToolHandler:
  """内置工具处理器"""

  builtin_tool_service: BuiltinToolService

  def get_builtin_tools(self):
    """获取LLMOps所有内置提供商＋工具信息"""
    builtin_tools = self.builtin_tool_service.get_builtin_tools()
    return success_json(builtin_tools)

  def get_provider_tool(self, provider_name: str, tool_name: str):
    """根据传递的提供商名字＋工具名字，获取指定的工具"""
    builtin_tool = self.builtin_tool_service.get_provider_tool(provider_name, tool_name)
    return success_json(builtin_tool)
