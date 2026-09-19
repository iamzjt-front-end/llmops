import json
import os
import uuid
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from flask import request
from injector import inject
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_deepseek import ChatDeepSeek
from redis import Redis

from internal.core.agent.agents import AgentQueueManager, FunctionCallAgent
from internal.core.agent.entities.agent_entity import AgentConfig
from internal.core.agent.entities.queue_entity import QueueEvent
from internal.core.tools.builtin_tools.providers import BuiltinProviderManager
from internal.entity.conversation_entity import InvokeFrom
from internal.exception import FailException
from internal.lib.chat_history import FileChatMessageHistory
from internal.schema.app_schema import CompletionReq
from internal.service import AppService
from pkg.response import (
  compact_generate_response,
  success_json,
  success_message,
  validate_error_json,
)


@inject
@dataclass
class AppHandler:
  """应用控制器"""

  app_service: AppService
  builtin_provider_manager: BuiltinProviderManager
  redis_client: Redis

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

    # SSE 按 Accept 协商，保留现有前端的 JSON 响应格式。
    if 'text/event-stream' not in request.headers.get('Accept', ''):
      return self._debug_completion(app_id, req.query.data)

    tools = []
    for provider, name, key in [
      ('google', 'google_serper', 'SERPER_API_KEY'),
      ('gaode', 'gaode_weather', 'GAODE_API_KEY'),
      ('dalle', 'dalle3', 'OPENAI_API_KEY'),
    ]:
      if os.getenv(key):
        tools.append(self.builtin_provider_manager.get_tool(provider, name)())
    history = self._get_chat_history(app_id)
    agent = FunctionCallAgent(
      AgentConfig(llm=self._get_llm(), tools=tools),
      AgentQueueManager(
        user_id=uuid.UUID('46db30d1-3199-4e79-a0cd-abf12fa6858f'),
        task_id=uuid.uuid4(),
        invoke_from=InvokeFrom.DEBUGGER,
        redis_client=self.redis_client,
      ),
    )

    def stream_event_response():
      answer = ''
      failed = False
      for event in agent.run(req.query.data, history.messages[-6:]):
        if event.event == QueueEvent.AGENT_MESSAGE:
          answer += event.answer
        if event.event in {QueueEvent.ERROR, QueueEvent.STOP, QueueEvent.TIMEOUT}:
          failed = True
        data = event.model_dump(mode='json', exclude={'messages'})
        yield f'event: {event.event.value}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n'
      if answer and not failed:
        history.add_user_message(req.query.data)
        history.add_ai_message(answer)

    return compact_generate_response(stream_event_response())

  @staticmethod
  def _get_chat_history(app_id: UUID):
    root = Path(__file__).resolve().parents[2] / 'storage' / 'memory'
    return FileChatMessageHistory(str(root / f'{app_id}.json'))

  @staticmethod
  def _get_llm():
    provider = os.getenv('CHAT_MODEL_PROVIDER', 'deepseek')
    if provider == 'openai':
      from langchain_openai import ChatOpenAI

      return ChatOpenAI(model=os.getenv('CHAT_MODEL', 'gpt-4o-mini'))
    if provider != 'deepseek':
      raise FailException('CHAT_MODEL_PROVIDER 必须是 deepseek 或 openai')
    return ChatDeepSeek(model=os.getenv('CHAT_MODEL', 'deepseek-v4-flash'))

  def _debug_completion(self, app_id: UUID, query: str):
    prompt = ChatPromptTemplate.from_messages(
      [
        ('system', '你是一个强大的聊天机器人，请根据用户的提问回复对应的问题。'),
        MessagesPlaceholder('history'),
        ('human', '{query}'),
      ]
    )
    history = self._get_chat_history(app_id)
    chain = prompt | self._get_llm() | StrOutputParser()
    content = chain.invoke({'query': query, 'history': history.messages[-6:]})
    history.add_user_message(query)
    history.add_ai_message(content)
    return success_json({'content': content})

  def ping(self):
    return success_json()
    # raise FailException('数据未找到')
