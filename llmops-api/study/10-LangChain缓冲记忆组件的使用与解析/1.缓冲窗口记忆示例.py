import sys
from operator import itemgetter

import dotenv
from langchain_classic.memory import (
  ConversationBufferWindowMemory,
  ConversationTokenBufferMemory,
)
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_deepseek import ChatDeepSeek

dotenv.load_dotenv()

# 1.创建提示模板&记忆 & 记忆
prompt = ChatPromptTemplate.from_messages(
  [
    ('system', '你是个聊天机器人，请根据上下文回复用户的问题'),
    MessagesPlaceholder('history'),  # 需要的history是一个列表
    ('human', '{query}'),
  ]
)
# memory = ConversationBufferWindowMemory(k=2, return_messages=True, input_key='query')
memory = ConversationTokenBufferMemory(llm=ChatDeepSeek(model='deepseek-v4-flash'))

# 2.创建大语言模型
llm = ChatDeepSeek(model='deepseek-v4-flash')

# 3.构建链应用
chain = (
  RunnablePassthrough.assign(
    history=RunnableLambda(memory.load_memory_variables) | itemgetter('history')
  )
  | prompt
  | llm
  | StrOutputParser()
)

# 4.死循环构建对话命令行
while True:
  query = input('Human: ')

  if query == 'q':
    sys.exit(0)

  chain_input = {'query': query}
  response = chain.stream(chain_input)

  print('AI: ', flush=True, end='')

  output = ''
  for chunk in response:
    output += chunk
    print(chunk, flush=True, end='')

  memory.save_context(chain_input, {'output': output})
  print()
  print('history: ', memory.load_memory_variables({}))
