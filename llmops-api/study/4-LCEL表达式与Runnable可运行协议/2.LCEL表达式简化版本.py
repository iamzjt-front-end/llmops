import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_deepseek import ChatDeepSeek

dotenv.load_dotenv()

# 1.构建组件
prompt = ChatPromptTemplate.from_template('{query}')
llm = ChatDeepSeek(model='deepseek-v4-flash')
parser = StrOutputParser()

# 2.创建链
chain = prompt | llm | parser

# 3.调用链并输出结果
print(chain.invoke({'query': '你好'}))
