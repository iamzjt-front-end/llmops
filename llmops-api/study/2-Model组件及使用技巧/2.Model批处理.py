from datetime import UTC, datetime

import dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_deepseek import ChatDeepSeek

dotenv.load_dotenv()

# 1.编排prompt
prompt = ChatPromptTemplate.from_messages(
  [
    (
      'system',
      '你是OpenAI开发的聊天机器人，请根据用户的提问进行回复，现在的时间是{now}',
    ),
    ('human', '{query}'),
  ]
).partial(now=datetime.now(UTC))

# 2.创建大语言模型
llm = ChatDeepSeek(model='deepseek-v4-flash')

ai_messages = llm.batch(
  [
    prompt.invoke({'query': '你好，你是？'}),
    prompt.invoke({'query': '请讲一个关于程序员的冷笑话'}),
  ]
)

for ai_message in ai_messages:
  print(ai_message.content)
  print('================')
