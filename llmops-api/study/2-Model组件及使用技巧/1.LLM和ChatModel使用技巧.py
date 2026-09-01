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

ai_message = llm.invoke(prompt.invoke({'query': '现在是几点，请讲一个程序员的冷笑话'}))

print(ai_message.type)
print(ai_message.content)
print(ai_message.response_metadata)
