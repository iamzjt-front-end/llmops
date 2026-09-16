import json
from dataclasses import dataclass
from typing import Any

from exception import ValidateErrorException
from injector import inject


@inject
@dataclass
class APIToolService:
  """自定义API插件服务"""

  @classmethod
  def parser_openapi_schema(cls, openapi_schema_str: str) -> Any:
    """解析传递的openai_schema字符串，如果出错则抛出错误"""
    try:
      data = json.loads(openapi_schema_str)
      if not isinstance(data, dict):
        raise
    except Exception as e:
      raise ValidateErrorException('传递数据必须符合OpenAPI规范的JSON字符串')
