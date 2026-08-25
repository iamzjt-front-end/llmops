import os

from openai import OpenAI
from openai.types.chat import (
  ChatCompletionMessageParam,
  ChatCompletionSystemMessageParam,
  ChatCompletionUserMessageParam,
)

from internal.exception import FailException
from internal.schema.app_schema import CompletionReq
from pkg.response import success_json, validate_error_json


class AppHandler:
  """应用控制器"""

  def completion(self):
    """聊天接口"""
    # 1.提取从接口中获取的输入，POST
    req = CompletionReq()
    if not req.validate():
      return validate_error_json(req.errors)

    # 2.构建OpenAI客户端，并发起请求
    client = OpenAI(base_url=os.getenv('OPENAI_API_BASE'))

    system_message: ChatCompletionSystemMessageParam = {
      'role': 'system',
      'content': '你是OpenAI开发的聊天机器人，请根据用户的输入回复对应的信息',
    }
    user_message: ChatCompletionUserMessageParam = {
      'role': 'user',
      'content': req.query.data or '',
    }
    messages: list[ChatCompletionMessageParam] = [
      system_message,
      user_message,
    ]

    # 3.得到请求响应，然后将OpenAI的响应传递给前端
    completion = client.chat.completions.create(
      model='deepseek-v4-flash',
      messages=messages,
    )

    content = completion.choices[0].message.content
    return success_json({'content': content})

  def ping(self):
    raise FailException('数据未找到')
