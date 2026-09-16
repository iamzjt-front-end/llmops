// api请求接口前缀
export const apiPrefix: string = 'http://localhost:5001'

// 业务状态码
export const httpCode = {
  success: 'success',
  fail: 'fail',
  notFound: 'not_found',
  unauthorized: 'unauthorized',
  forbidden: 'forbidden',
  validateError: 'validate_error',
}

// 工具参数类型与中文名称映射
export const typeMap: Record<string, string> = {
  str: '字符串',
  string: '字符串',
  int: '整型',
  integer: '整型',
  float: '浮点型',
  number: '数值',
  bool: '布尔值',
  boolean: '布尔值',
  list: '列表',
  array: '列表',
  dict: '对象',
  object: '对象',
}
