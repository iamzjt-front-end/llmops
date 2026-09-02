from operator import itemgetter

import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel
from langchain_deepseek import ChatDeepSeek

dotenv.load_dotenv()


def retrieval(query: str) -> str:
  """一个模拟的检索器函数"""
  print('正在检索:', query)
  return '我是J.Tide'


# 1.编排prompt
prompt = ChatPromptTemplate.from_template("""请根据用户的提问进行回答，可以参考对应的上下文进行生成。

<context>
{context}
</context>

用户的提问是: {query}""")

# 2.构建大语言模型
llm = ChatDeepSeek(model='deepseek-v4-flash')

# 3.输出解析器
parser = StrOutputParser()

# 4.构建链
chain = (
  RunnableParallel(
    {
      'context': lambda x: retrieval(x['query']),
      'query': itemgetter('query'),
    }
  )
  | prompt
  | llm
  | parser
)

# 5.调用链
content = chain.invoke({'query': '你好，我是谁？'})
print(content)
