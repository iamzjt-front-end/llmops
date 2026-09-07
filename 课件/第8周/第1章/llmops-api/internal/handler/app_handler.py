#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/3/29 14:59
@Author  : thezehui@gmail.com
@File    : app_handler.py
"""
import json
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Generator
from uuid import UUID

from injector import inject
from langchain_core.documents import Document
from langchain_core.memory import BaseMemory
from langchain_core.runnables import RunnableConfig
from langchain_core.tracers import Run
from langchain_openai import ChatOpenAI
from redis import Redis

from internal.core.agent.agents import FunctionCallAgent, AgentQueueManager
from internal.core.agent.entities.agent_entity import AgentConfig
from internal.core.tools.builtin_tools.providers import BuiltinProviderManager
from internal.entity.conversation_entity import InvokeFrom
from internal.schema.app_schema import CompletionReq
from internal.service import AppService, VectorDatabaseService, ApiToolService, EmbeddingsService, ConversationService
from pkg.response import success_json, validate_error_json, success_message, compact_generate_response


@inject
@dataclass
class AppHandler:
    """应用控制器"""
    app_service: AppService
    vector_database_service: VectorDatabaseService
    api_tool_service: ApiToolService
    embeddings_service: EmbeddingsService
    builtin_provider_manager: BuiltinProviderManager
    conversation_service: ConversationService
    redis_client: Redis

    def create_app(self):
        """调用服务创建新的APP记录"""
        app = self.app_service.create_app()
        return success_message(f"应用已经成功创建，id为{app.id}")

    def get_app(self, id: uuid.UUID):
        app = self.app_service.get_app(id)
        return success_message(f"应用已经成功获取，名字是{app.name}")

    def update_app(self, id: uuid.UUID):
        app = self.app_service.update_app(id)
        return success_message(f"应用已经成功修改，修改的名字是:{app.name}")

    def delete_app(self, id: uuid.UUID):
        app = self.app_service.delete_app(id)
        return success_message(f"应用已经成功删除，id为:{app.id}")

    @classmethod
    def _load_memory_variables(cls, input: Dict[str, Any], config: RunnableConfig) -> Dict[str, Any]:
        """加载记忆变量信息"""
        configurable = config.get("configurable", {})
        configurable_memory = configurable.get("memory", None)
        if configurable_memory is not None and isinstance(configurable_memory, BaseMemory):
            return configurable_memory.load_memory_variables(input)
        return {"history": []}

    @classmethod
    def _save_context(cls, run_obj: Run, config: RunnableConfig) -> None:
        """存储对应的上下文信息到记忆实体中"""
        configurable = config.get("configurable", {})
        configurable_memory = configurable.get("memory", None)
        if configurable_memory is not None and isinstance(configurable_memory, BaseMemory):
            configurable_memory.save_context(run_obj.inputs, run_obj.outputs)

    def debug(self, app_id: UUID):
        """应用会话调试聊天接口，该接口为流式事件输出"""
        # 1.提取从接口中获取的输入，POST
        req = CompletionReq()
        if not req.validate():
            return validate_error_json(req.errors)

        # 2.定义工具列表
        tools = [
            self.builtin_provider_manager.get_tool("google", "google_serper")(),
            self.builtin_provider_manager.get_tool("gaode", "gaode_weather")(),
            self.builtin_provider_manager.get_tool("dalle", "dalle3")(),
        ]

        agent = FunctionCallAgent(
            AgentConfig(
                llm=ChatOpenAI(model="gpt-4o-mini"),
                enable_long_term_memory=True,
                tools=tools,
            ),
            AgentQueueManager(
                user_id=uuid.uuid4(),
                task_id=uuid.uuid4(),
                invoke_from=InvokeFrom.DEBUGGER,
                redis_client=self.redis_client,
            )
        )

        def stream_event_response() -> Generator:
            """流式事件输出响应"""
            for agent_queue_event in agent.run(req.query.data, [], "用户介绍自己叫慕小课"):
                data = {
                    "id": str(agent_queue_event.id),
                    "task_id": str(agent_queue_event.task_id),
                    "event": agent_queue_event.event,
                    "thought": agent_queue_event.thought,
                    "observation": agent_queue_event.observation,
                    "tool": agent_queue_event.tool,
                    "tool_input": agent_queue_event.tool_input,
                    "answer": agent_queue_event.answer,
                    "latency": agent_queue_event.latency
                }
                yield f"event: {agent_queue_event.event}\ndata: {json.dumps(data)}\n\n"

        return compact_generate_response(stream_event_response())

    @classmethod
    def _combine_documents(cls, documents: list[Document]) -> str:
        """将传入的文档列表合并成字符串"""
        return "\n\n".join([document.page_content for document in documents])

    def ping(self):
        from internal.core.agent.agents import FunctionCallAgent
        from internal.core.agent.entities.agent_entity import AgentConfig
        from langchain_openai import ChatOpenAI

        agent = FunctionCallAgent(AgentConfig(
            llm=ChatOpenAI(model="gpt-4o-mini"),
            preset_prompt="你是一个拥有20年经验的诗人，请根据用户提供的主题来写一首诗"
        ))
        state = agent.run("程序员", [], "")
        content = state["messages"][-1].content

        return success_json({"content": content})
