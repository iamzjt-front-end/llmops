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

    # 2.构建组件
    prompt = ChatPromptTemplate.from_template('{query}')
    llm = ChatDeepSeek(model='deepseek-v4-flash')
    parser = StrOutputParser()

    # 3.构建链
    chain = prompt | llm | parser

    # 4.调用链得到结果
    content = chain.invoke({'query': req.query.data})

    return success_json({'content': content})

  def ping(self):
    raise FailException('数据未找到')
