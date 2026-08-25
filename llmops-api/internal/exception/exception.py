from typing import Any

from pkg.response import HttpCode


class CustomException(Exception):
  """基础自定义异常信息"""

  code: HttpCode = HttpCode.FAIL

  def __init__(self, message: str | None = None, data: Any = None):
    normalized_message = message or ''
    super().__init__(normalized_message)
    self.message = normalized_message
    self.data = {} if data is None else data


class FailException(CustomException):
  """通用失败异常"""

  pass


class NotFoundException(CustomException):
  """未找到异常"""

  code = HttpCode.NOT_FOUND


class UnauthorizedException(CustomException):
  """未授权异常"""

  code = HttpCode.UNAUTHORIZED


class ForbiddenException(CustomException):
  """无权限异常"""

  code = HttpCode.FORBIDDEN


class ValidateErrorException(CustomException):
  """数据验证异常"""

  code = HttpCode.VALIDATE_ERROR
