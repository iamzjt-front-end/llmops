import sys

import dotenv
from langchain_core.messages import AIMessageChunk, HumanMessage, SystemMessage
from langchain_deepseek import ChatDeepSeek
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph

dotenv.load_dotenv()

# 1.定义大语言模型
llm = ChatDeepSeek(model='deepseek-v4-flash')

# 2.定义状态图：MessagesState 自带 messages 字段，
#   内部的 add_messages 汇聚器会自动把新消息【增量追加】到历史里，无需手动维护
builder = StateGraph(MessagesState)


# 3.定义聊天节点：系统提示不放进 state（避免重复写入历史），每次调用时拼接
def chatbot(state: MessagesState):
  system_message = SystemMessage(
    content='你是一个强大的聊天机器人，请根据用户的需求回复问题。'
  )
  return {'messages': [llm.invoke([system_message, *state['messages']])]}


builder.add_node('chatbot', chatbot)
builder.add_edge(START, 'chatbot')

# 4.编译图并挂载内置持久化：MemorySaver 基于内存存储，
#   每个 thread_id 对应一份独立的会话历史（等价于原来的 session_id）
#   如需像 FileChatMessageHistory 一样跨进程持久化，
#   可换成 langgraph-checkpoint-sqlite 提供的 SqliteSaver
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

while True:
  query = input('Human: ')

  if query == 'q':
    sys.exit(0)

  # 5.运行图并传递配置信息，stream_mode='messages' 可以拿到节点内部大模型的流式 token
  config = {'configurable': {'thread_id': 'muxiaoke'}}
  print('AI: ', flush=True, end='')
  for chunk, metadata in graph.stream(
    {'messages': [HumanMessage(content=query)]},
    config,
    stream_mode='messages',
  ):
    # 只输出聊天节点里大模型产生的流式内容
    if isinstance(chunk, AIMessageChunk) and chunk.content:
      print(chunk.content, flush=True, end='')
  print()
