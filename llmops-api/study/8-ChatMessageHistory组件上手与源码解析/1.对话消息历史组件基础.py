from langchain_core.chat_history import InMemoryChatMessageHistory

chat_history = InMemoryChatMessageHistory()
chat_history.add_user_message('你好，我是zjt，你是谁？')
chat_history.add_ai_message('你好，我是deepseek，有什么可以帮到您？')

print(chat_history)
