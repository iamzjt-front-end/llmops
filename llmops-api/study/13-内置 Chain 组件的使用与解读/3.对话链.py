import dotenv
from langchain_classic.chains.conversation.base import ConversationChain
from langchain_deepseek import ChatDeepSeek

dotenv.load_dotenv()

llm = ChatDeepSeek(model='deepseek-v4-flash')
chain = ConversationChain(llm=llm)

content = chain.invoke(
  {'input': '你好，我是慕小课，我喜欢打篮球还有游泳，你喜欢什么运动呢？'}
)

print(content)

content = chain.invoke({'input': '根据上下文信息，请统计一下我的运动爱好有什么?'})

print(content)
