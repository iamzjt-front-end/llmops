import os
import uuid
from dataclasses import dataclass

from injector import inject
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_deepseek import ChatDeepSeek
from openai import OpenAI
from openai.types.chat import (
  ChatCompletionMessageParam,
  ChatCompletionSystemMessageParam,
  ChatCompletionUserMessageParam,
)

from internal.exception import FailException
from internal.schema.app_schema import CompletionReq
from internal.service import AppService
from pkg.response import success_json, success_message, validate_error_json


@inject
@dataclass
class AppHandler:
  """应用控制器"""

  app_service: AppService

  def create_app(self):
    """调用服务创建新的App记录"""
    app = self.app_service.create_app()
    return success_message(f'应用已经创建成功，id为{app.id}')

  def get_app(self, id: uuid.UUID):
    app = self.app_service.get_app(id)
    return success_message(f'应用已经成功获取，名字是{app.name}')

  def update_app(self, id: uuid.UUID):
    app = self.app_service.update_app(id)
    return success_message(f'应用已经成功修改，修改的名字是{app.name}')

  def delete_app(self, id: uuid.UUID):
    app = self.app_service.delete_app(id)
    return success_message(f'{app.name}应用已经成功删除')

  def completion(self):
    """聊天接口"""
    # 1.提取从接口中获取的输入
    req = CompletionReq()
    if not req.validate():
      return validate_error_json(req.errors)

    prompt = ChatPromptTemplate.from_template('{query}')

    # 2.构建大语言模型，并发起请求
    llm = ChatDeepSeek(model='deepseek-v4-flash')

    # 3.得到请求响应，然后将OpenAI的响应传递给前端
    ai_message = llm.invoke(prompt.invoke({'query': req.query.data}))

    # 4.解析响应内容
    parser = StrOutputParser()
    content = parser.invoke(ai_message)

    return success_json({'content': content})

  def ping(self):
    raise FailException('数据未找到')
