from dataclasses import dataclass
from typing import Any
from uuid import UUID

from injector import inject
from langchain_classic.base_memory import BaseMemory
from langchain_classic.memory import ConversationBufferWindowMemory
from langchain_community.chat_message_histories import FileChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableConfig, RunnableLambda, RunnablePassthrough
from langchain_core.tracers import Run
from langchain_deepseek import ChatDeepSeek

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

  def get_app(self, app_id: UUID):
    app = self.app_service.get_app(app_id)
    return success_message(f'应用已经成功获取，名字是{app.name}')

  def update_app(self, app_id: UUID):
    app = self.app_service.update_app(app_id)
    return success_message(f'应用已经成功修改，修改的名字是{app.name}')

  def delete_app(self, app_id: UUID):
    app = self.app_service.delete_app(app_id)
    return success_message(f'{app.name}应用已经成功删除')

  @classmethod
  def _load_memory_variables(
    cls, input: dict[str, Any], config: RunnableConfig
  ) -> dict[str, Any]:
    """加载记忆变量信息"""
    # 1.从config中获取configurable
    configurable = config.get('configurable', {})
    configurable_memory = configurable.get('memory', {})

    if configurable_memory is not None and isinstance(configurable_memory, BaseMemory):
      return configurable_memory.load_memory_variables(input)
    return {'history': []}

  @staticmethod
  def _get_history(memory_variables: dict[str, Any]) -> Any:
    """提取提示词所需的历史消息。"""
    return memory_variables['history']

  @staticmethod
  def _save_context(run_obj: Run, memory: BaseMemory) -> None:
    """存储对应的上下文信息到记忆实体中"""
    if run_obj.outputs is not None:
      memory.save_context(run_obj.inputs, run_obj.outputs)

  def debug(self, app_id: UUID):
    """聊天接口"""
    # 1.提取从接口中获取的输入
    req = CompletionReq()
    if not req.validate():
      return validate_error_json(req.errors)

    # 2.创建prompt与记忆
    prompt = ChatPromptTemplate.from_messages(
      [
        ('system', '你是一个强大的聊天机器人，请根据用户的提问回复对应的问题。'),
        MessagesPlaceholder('history'),
        ('human', '{query}'),
      ]
    )
    memory = ConversationBufferWindowMemory(
      k=3,
      input_key='query',
      output_key='output',
      return_messages=True,
      chat_memory=FileChatMessageHistory('./storage/memory/chat_history.txt'),
    )

    # 3.创建llm
    llm = ChatDeepSeek(model='deepseek-v4-flash')

    def on_end(run_obj: Run) -> None:
      self._save_context(run_obj, memory)

    # 4.构建链
    chain = (
      RunnablePassthrough.assign(
        history=RunnableLambda(self._load_memory_variables)
        | RunnableLambda(self._get_history)
      )
      | prompt
      | llm
      | StrOutputParser()
    ).with_listeners(on_end=on_end)

    # 5.调用链得到结果
    chain_input = {'query': req.query.data}
    chain_config: RunnableConfig = {
      'configurable': {
        'memory': memory,
      },
    }
    content = chain.invoke(
      chain_input,
      config=chain_config,
    )

    return success_json({'content': content})

  def ping(self):
    raise FailException('数据未找到')
