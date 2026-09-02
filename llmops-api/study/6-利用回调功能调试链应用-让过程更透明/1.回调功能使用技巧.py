import time
from typing import Any
from uuid import UUID

import dotenv
from langchain_core.callbacks import BaseCallbackHandler, StdOutCallbackHandler
from langchain_core.messages import BaseMessage, ChatMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.outputs import ChatGenerationChunk, GenerationChunk, LLMResult
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_deepseek import ChatDeepSeek

dotenv.load_dotenv()


class LLMOpsCallBackHandler(BaseCallbackHandler):
  """自定义LLMOps回调处理器"""

  start_at: float = 0

  def on_chat_model_start(
    self,
    serialized: dict[str, Any],
    messages: list[list[BaseMessage]],
    *,
    run_id: UUID,
    parent_run_id: UUID | None = None,
    tags: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
    **kwargs: Any,
  ) -> Any:
    print('聊天模型开始执行')
    print('serialized:', serialized)
    print('messages:', messages)
    self.start_at = time.time()

  def on_llm_end(
    self,
    response: LLMResult,
    *,
    run_id: UUID,
    parent_run_id: UUID | None = None,
    tags: list[str] | None = None,
    **kwargs: Any,
  ) -> Any:
    end_at: float = time.time()
    print(f'程序消耗：{end_at - self.start_at}')
    print(f'完整输出：{response}')


# 1.构建组件
prompt = ChatPromptTemplate.from_template('{query}')

# 2.构建大语言模型
llm = ChatDeepSeek(model='deepseek-v4-flash')

# 2.构建链
chain = {'query': RunnablePassthrough()} | prompt | llm | StrOutputParser()

# 3.调用链并输出结果
resp = chain.stream(
  '你好', config={'callbacks': [StdOutCallbackHandler(), LLMOpsCallBackHandler()]}
)

for chunk in resp:
  pass
