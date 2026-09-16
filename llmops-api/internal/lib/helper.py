import importlib
from typing import Any


def dynamic_import(module_name: str, symbol_name: str) -> Any:
  """动态导入特定模块下的特定功能"""
  module = importlib.import_module(module_name)
  return getattr(module, symbol_name)


def add_attribute(attr_name: str, attr_value: Any):
  """装饰器函数，为函数增加相应的属性"""

  def decorator(func):
    setattr(func, attr_name, attr_value)
    return func

  return decorator
