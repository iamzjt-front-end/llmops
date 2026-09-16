from dataclasses import dataclass
from uuid import UUID

from injector import inject
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_deepseek import ChatDeepSeek

from internal.core.tools.builtin_tools.providers import BuiltinProviderManager
from internal.lib.chat_history import FileChatMessageHistory
from internal.schema.app_schema import CompletionReq
from internal.service import AppService
from pkg.response import success_json, success_message, validate_error_json


@inject
@dataclass
class AppHandler:
  """应用控制器"""

  app_service: AppService
  builtin_provider_manager: BuiltinProviderManager

  def create_app(self):
    """调用服务创建新的App记录"""
    app = self.app_service.create_app()
    return success_message(f'应用已经创建成功，id为{app.id}')

  def get_app(self, app_id: UUID):
    app = self.app_service.get_app(app_id)
    return success_message(f'应用已经成功获取，名字是{app.name}')

  def update_app(self, app_id: UUID):
    app = self.app_service.update_app(app_id)
    return success_message(f'应用已经成功修改，修改的名字是{app.name}')

  def delete_app(self, app_id: UUID):
    app = self.app_service.delete_app(app_id)
    return success_message(f'{app.name}应用已经成功删除')

  def debug(self, app_id: UUID):
    """聊天接口"""
    # 1.提取从接口中获取的输入
    req = CompletionReq()
    if not req.validate():
      return validate_error_json(req.errors)

    # 2.创建提示词
    prompt = ChatPromptTemplate.from_messages(
      [
        ('system', '你是一个强大的聊天机器人，请根据用户的提问回复对应的问题。'),
        MessagesPlaceholder('history'),
        ('human', '{query}'),
      ]
    )

    # 3.加载文件持久化的对话历史，取最近 3 轮（6 条消息）作为上下文窗口
    chat_history = FileChatMessageHistory('./storage/memory/chat_history.txt')
    history = chat_history.messages[-6:]

    # 4.创建llm
    llm = ChatDeepSeek(model='deepseek-v4-flash')

    # 5.构建链并调用得到结果
    chain = prompt | llm | StrOutputParser()
    content = chain.invoke({'query': req.query.data, 'history': history})

    # 6.将本轮对话追加到历史文件中
    chat_history.add_user_message(req.query.data)
    chat_history.add_ai_message(content)

    return success_json({'content': content})

  def ping(self):
    return success_json()
    # raise FailException('数据未找到')
