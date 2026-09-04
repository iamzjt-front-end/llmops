import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_deepseek import ChatDeepSeek

dotenv.load_dotenv()

prompt = ChatPromptTemplate.from_messages(
  [
    ('system', '请直接回答用户的问题，不要复述用户原话。'),
    ('human', '{query}'),
  ]
)
# llm = ChatDeepSeek(model='deepseek-v4-flash', stop_sequences='世界')
llm = ChatDeepSeek(model='deepseek-v4-flash')

# chain = prompt | llm.bind(stop='world') | StrOutputParser()
chain = prompt | llm.bind(model='deepseek-v4-pro') | StrOutputParser()
content = chain.invoke(
  {
    'query': '你是什么模型？',
  }
)

print(content)
