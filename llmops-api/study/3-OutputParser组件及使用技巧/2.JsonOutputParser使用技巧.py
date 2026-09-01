import dotenv
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_deepseek import ChatDeepSeek
from pydantic import BaseModel, Field

dotenv.load_dotenv()


# 1.创建一个json数据结构，用于告诉大预言模型这个json长什么样子
class Joke(BaseModel):
  # 冷笑话
  joke: str = Field(description='回答用户的冷笑话')
  # 冷笑话的笑点
  punchline: str = Field(description='这个冷笑话的笑点')


parser = JsonOutputParser(pydantic_object=Joke)

# 2.构建一个提示模版
prompt = ChatPromptTemplate.from_template(
  '请根据用户的提问进行回答。\n{format_instructions}\n{query}'
).partial(format_instructions=parser.get_format_instructions())

# 3.创建大语言模型
llm = ChatDeepSeek(model='deepseek-v4-flash')

# 4.传递提示并进行解析
joke = parser.invoke(llm.invoke(prompt.invoke({'query': '请讲一个关于程序员的冷笑话'})))

print(type(joke))
print(joke.get('punchline'))
print(joke)
