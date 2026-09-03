import os

import dotenv
from langchain_community.chat_message_histories import FileChatMessageHistory
from openai import OpenAI

dotenv.load_dotenv()

# 1.创建openai客户端
client = OpenAI(
  api_key=os.environ.get('DEEPSEEK_API_KEY'),
  base_url=os.environ.get('DEEPSEEK_API_BASE'),
)
chat_history = FileChatMessageHistory(file_path='./memory.txt')

# 2.创建一个死循环用于人机对话
while True:
  # 3.获取人类输入
  query = input('Human: ')

  # 4.判断下输入是否为q，如果是则退出
  if query == 'q':
    break

  # 5.向openai的接口发起请求，获取AI生成的内容
  print('AI: ', flush=True, end='')
  system_prompt = (
    '你是个聊天机器人，可以根据相应的上下文回复用户信息，上下文里面存放的是人类与你对话的信息列表\n\n'
    f'f"<context>{chat_history}</context>\n\n"'
  )
  response = client.chat.completions.create(
    model='deepseek-v4-flash',
    messages=[
      {'role': 'system', 'content': system_prompt},
      {'role': 'user', 'content': query},
    ],
    stream=True,
  )

  # 6.循环读取流式响应的内容
  ai_content = ''
  for chunk in response:
    content = chunk.choices[0].delta.content
    if content is not None:
      ai_content += content
      print(content, flush=True, end='')
  chat_history.add_user_message(query)
  chat_history.add_ai_message(ai_content)
  print()
