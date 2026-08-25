from dataclasses import dataclass, field
from typing import Any

from flask import jsonify

from .http_code import HttpCode


@dataclass
class Response:
  """基础 HTTP 接口响应格式"""

  code: HttpCode = HttpCode.SUCCESS
  message: str = ''
  data: Any = field(default_factory=dict)


def json(data: Response | None = None):
  """基础的响应接口"""
  return jsonify(data), 200


def success_json(data: Any = None):
  """成功数据响应"""
  return json(Response(code=HttpCode.SUCCESS, message='', data=data))


def fail_json(data: Any = None):
  """失败数据响应"""
  return json(Response(code=HttpCode.FAIL, message='', data=data))


def validate_error_json(errors: dict | None = None):
  """数据验证错误响应"""
  errors = errors or {}
  first_error = next(iter(errors.values()), [])
  message = first_error[0] if first_error else ''
  return json(
    Response(
      code=HttpCode.VALIDATE_ERROR,
      message=message,
      data=errors,
    )
  )


def message(code: HttpCode | None = None, msg: str = ''):
  """基础的消息响应，固定返回消息提示，数据固定为空字典"""
  return json(Response(code=code, message=msg, data={}))


def success_message(msg: str = ''):
  """成功的基础消息响应"""
  return message(HttpCode.SUCCESS, msg=msg)


def fail_message(msg: str = ''):
  """失败的消息响应"""
  return message(HttpCode.FAIL, msg=msg)


def not_found_message(msg: str = ''):
  """未找到的消息响应"""
  return message(HttpCode.NOT_FOUND, msg=msg)


def unauthorized_message(msg: str = ''):
  """未授权的消息响应"""
  return message(HttpCode.UNAUTHORIZED, msg=msg)


def forbidden_message(msg: str = ''):
  """无权限的消息响应"""
  return message(HttpCode.FORBIDDEN, msg=msg)
