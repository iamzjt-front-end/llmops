import dotenv
from langchain_community.chat_models.baidu_qianfan_endpoint import QianfanChatEndpoint
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_deepseek import ChatDeepSeek

dotenv.load_dotenv()

# 1.构建prompt与LLM，并将model切换为gpt-3.5-turbo-18k引发出错
prompt = ChatPromptTemplate.from_template('{query}')
llm = ChatDeepSeek(model='gpt-3.5-turbo-18k').with_fallbacks([QianfanChatEndpoint()])

# 2.构建链应用
chain = prompt | llm | StrOutputParser()

# 3.调用链并输出结果
content = chain.invoke({'query': '你好，你是?'})
print(content)
