import json
from dataclasses import dataclass

from injector import inject

from internal.core.tools.api_tools.entities.openapi_schema import OpenAPISchema
from internal.exception import ValidateErrorException


@inject
@dataclass
class APIToolService:
  """自定义API插件服务"""

  @staticmethod
  def parser_openapi_schema(openapi_schema_str: str) -> OpenAPISchema:
    """解析传递的openapi_schema字符串，如果出错则抛出错误"""
    try:
      data = json.loads(openapi_schema_str.strip())
    except json.JSONDecodeError as exc:
      raise ValidateErrorException('传递数据必须符合OpenAPI规范的JSON字符串') from exc

    if not isinstance(data, dict):
      raise ValidateErrorException('传递数据必须符合OpenAPI规范的JSON字符串')

    return OpenAPISchema.model_validate(data)
