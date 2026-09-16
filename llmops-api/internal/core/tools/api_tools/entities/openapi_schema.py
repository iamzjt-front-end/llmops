from enum import Enum

from pydantic import BaseModel, Field, field_validator

from internal.exception import ValidateErrorException


class ParameterType(str, Enum):
  """参数支持的类型"""

  STR = 'str'
  INT = 'int'
  FLOAT = 'float'
  BOOL = 'bool'


ParameterTypeMap = {
  ParameterType.STR: str,
  ParameterType.INT: int,
  ParameterType.FLOAT: float,
  ParameterType.BOOL: bool,
}


class ParameterIn(str, Enum):
  """参数支持存放的位置"""

  PATH = 'path'
  QUERY = 'query'
  HEADER = 'header'
  COOKIE = 'cookie'
  REQUEST_BODY = 'request_body'


def _validate_parameter(parameter: dict) -> None:
  """校验接口参数的必填字段与字段类型。"""
  if not isinstance(parameter.get('name'), str):
    raise ValidateErrorException('parameter.name参数必须为字符串且不为空')
  if not isinstance(parameter.get('description'), str):
    raise ValidateErrorException('parameter.description参数必须为字符串且不为空')
  if not isinstance(parameter.get('required'), bool):
    raise ValidateErrorException('parameter.required参数必须为布尔值且不为空')
  if (
    not isinstance(parameter.get('in'), str)
    or parameter.get('in') not in ParameterIn.__members__.values()
  ):
    raise ValidateErrorException(
      f'parameter.in参数必须为{"/".join([item.value for item in ParameterIn])}'
    )
  if (
    not isinstance(parameter.get('type'), str)
    or parameter.get('type') not in ParameterType.__members__.values()
  ):
    raise ValidateErrorException(
      f'parameter.type参数必须为{"/".join([item.value for item in ParameterType])}'
    )


def _validate_operation(operation: dict, operation_ids: list[str]) -> None:
  """校验接口定义及其 operationId 和 parameters。"""
  if not isinstance(operation.get('description'), str):
    raise ValidateErrorException('description不能为空且为字符串')
  if not isinstance(operation.get('operationId'), str):
    raise ValidateErrorException('operationId不能为空且为字符串')
  if not isinstance(operation.get('parameters', []), list):
    raise ValidateErrorException('parameters必须是列表或者为空')

  operation_id = operation['operationId']
  if operation_id in operation_ids:
    raise ValidateErrorException(f'operationId必须唯一，{operation_id}出现重复')
  operation_ids.append(operation_id)

  for parameter in operation.get('parameters', []):
    _validate_parameter(parameter)


def _build_operation(operation: dict) -> dict:
  """提取工具执行所需的接口字段。"""
  return {
    'description': operation['description'],
    'operationId': operation['operationId'],
    'parameters': [
      {
        'name': parameter.get('name'),
        'in': parameter.get('in'),
        'description': parameter.get('description'),
        'required': parameter.get('required'),
        'type': parameter.get('type'),
      }
      for parameter in operation.get('parameters', [])
    ],
  }


class OpenAPISchema(BaseModel):
  """OpenAPI规范的数据结构"""

  server: str = Field(
    default='', validate_default=True, description='工具提供者的服务基础地址'
  )
  description: str = Field(
    default='', validate_default=True, description='工具提供者的描述信息'
  )
  paths: dict[str, dict] = Field(
    default_factory=dict, validate_default=True, description='工具提供者的路径参数字典'
  )

  @field_validator('server', mode='before')
  @classmethod
  def validate_server(cls, server: str) -> str:
    """校验server数据"""
    if server is None or server == '':
      raise ValidateErrorException('server不能为空且为字符串')
    return server

  @field_validator('description', mode='before')
  @classmethod
  def validate_description(cls, description: str) -> str:
    """校验description信息"""
    if description is None or description == '':
      raise ValidateErrorException('description不能为空且为字符串')
    return description

  @field_validator('paths', mode='before')
  @classmethod
  def validate_paths(cls, paths: dict[str, dict]) -> dict[str, dict]:
    """校验paths信息，涵盖：方法提取、operationId唯一标识，parameters校验"""
    # 1.paths不能为空且类型为字典
    if not paths or not isinstance(paths, dict):
      raise ValidateErrorException('openapi_schema中的paths不能为空且必须为字典')

    # 2.提取paths里的每一个元素，并校验get/post方法对应的值
    methods = ['get', 'post']
    extra_paths = {}
    operation_ids = []
    for path, path_item in paths.items():
      for method in methods:
        if method not in path_item:
          continue

        operation = path_item[method]
        _validate_operation(operation, operation_ids)
        extra_paths[path] = {method: _build_operation(operation)}

    return extra_paths
