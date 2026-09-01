from typing import Any

import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_deepseek import ChatDeepSeek

dotenv.load_dotenv()

# 1.构建组件
prompt = ChatPromptTemplate.from_template('{query}')
llm = ChatDeepSeek(model='deepseek-v4-flash')
parser = StrOutputParser()


# 2.定义链
class Chain:
  steps: list = []

  def __init__(self, steps: list):
    self.steps = steps

  def invoke(self, input: Any) -> Any:
    for step in self.steps:
      input = step.invoke(input)
      print('步骤：', step)
      print('输出：', input)
      print('===============')
    return input


# 3.编排链
chain = Chain([prompt, llm, parser])

# 4.执行链并输出结果
print(chain.invoke({'query': '你好'}))
