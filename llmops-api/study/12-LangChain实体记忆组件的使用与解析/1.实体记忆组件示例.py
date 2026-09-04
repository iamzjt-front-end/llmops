import dotenv
from langchain_classic.chains.conversation.base import ConversationChain
from langchain_classic.memory import ConversationEntityMemory
from langchain_classic.memory.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE
from langchain_community.chat_models.baidu_qianfan_endpoint import QianfanChatEndpoint

dotenv.load_dotenv()

# llm = ChatDeepSeek(model="gpt-4o", temperature=0)
llm = QianfanChatEndpoint()

chain = ConversationChain(
  llm=llm,
  prompt=ENTITY_MEMORY_CONVERSATION_TEMPLATE,
  memory=ConversationEntityMemory(llm=llm),
)

print(chain.invoke({'input': '你好，我是zjt。我最近正在学习LangChain。'}))
print(chain.invoke({'input': '我最喜欢的编程语言是 Python。'}))
print(chain.invoke({'input': '我住在广州'}))

# 查询实体中的对话
res = chain.memory.entity_store.store
print(res)
