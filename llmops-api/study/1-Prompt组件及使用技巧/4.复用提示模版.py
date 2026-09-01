from langchain_core.prompts import PromptTemplate

full_prompt = PromptTemplate.from_template("""{instruction}
{example}

{start}
""")

# 描述模版
instruction_prompt = PromptTemplate.from_template('你正在模拟{person}')

# 示例模版
example_prompt = PromptTemplate.from_template("""下面是一个交互例子：

Q: {example_q}
A: {example_a}""")

# 开始模版
start_prompt = PromptTemplate.from_template(
  """现在，你是一个真实的人，请回答用户的问题：
  
  Q: {input}
  A: """
)

pipeline_prompts = [
  ('instruction', instruction_prompt),
  ('example', example_prompt),
  ('start', start_prompt),
]


def build_prompt(values):
  rendered_prompts = {
    name: prompt.invoke(values).to_string() for name, prompt in pipeline_prompts
  }
  return full_prompt.invoke(rendered_prompts)


print(
  build_prompt(
    {
      'person': '雷军',
      'example_q': '你最喜欢的汽车是什么？',
      'example_a': '小米su7',
      'input': '你最喜欢的手机是什么',
    }
  ).to_string()
)
