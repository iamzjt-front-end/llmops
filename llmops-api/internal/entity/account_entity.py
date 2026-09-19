from enum import Enum


class AccountStatus(str, Enum):
  """账户状态类型枚举"""

  ACTIVE = 'active'  # 激活账号
  BANNED = 'banned'  # 封禁账号
