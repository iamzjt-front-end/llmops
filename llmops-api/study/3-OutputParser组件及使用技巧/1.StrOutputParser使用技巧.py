import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_deepseek import ChatDeepSeek

dotenv.load_dotenv()

# 1.编排prompt
prompt = ChatPromptTemplate.from_template('{query}')

# 2.创建大语言模型
llm = ChatDeepSeek(model='deepseek-v4-flash')

# 3.创建字符串输出解析器
parser = StrOutputParser()

# 4.调用LLM生成结果并解析
content = parser.invoke(llm.invoke(prompt.invoke({'query': '你好，你是？'})))
print(content)
