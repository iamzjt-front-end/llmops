#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/5/21 9:24
@Author  : thezehui@gmail.com
@File    : 1.摘要缓冲混合记忆.py.py
"""
from typing import Any

import dotenv
from openai import OpenAI

dotenv.load_dotenv()


# 1.max_tokens用于判断是否需要生成新的摘要
# 2.summary用于存储摘要的信息
# 3.chat_histories用于存储历史对话
# 4.get_num_tokens用于计算传入文本的token数
# 5.save_context用于存储新的交流对话
# 6.get_buffer_string用于将历史对话转换成字符串
# 7.load_memory_variables用于加载记忆变量信息
# 8.summary_text用于将旧的摘要和传入的对话生成新摘要
class ConversationSummaryBufferMemory:
    """摘要缓冲混合记忆类"""

    def __init__(self, summary: str = '', chat_histories: list = None, max_tokens: int = 300):
        self.summary = summary
        self.chat_histories = [] if chat_histories is None else chat_histories
        self.max_tokens = max_tokens
        self._client = OpenAI(base_url='https://api.xty.app/v1')

    @classmethod
    def get_num_tokens(cls, query: str) -> int:
        """计算传入的query的token数"""
        return len(query)

    def save_context(self, human_query: str, ai_content: str) -> None:
        """保存传入的新一次对话信息"""
        self.chat_histories.append({"human": human_query, "ai": ai_content})

        buffer_string = self.get_buffer_string()

        tokens = self.get_num_tokens(buffer_string)

        if tokens > self.max_tokens:
            first_chat = self.chat_histories[0]
            print("新摘要生成中~")
            self.summary = self.summary_text(
                self.summary,
                f"Human:{first_chat.get('human')}\nAI:{first_chat.get('ai')}"
            )
            print("新摘要生成成功:", self.summary)
            del self.chat_histories[0]

    def get_buffer_string(self) -> str:
        """将历史对话转换成字符串"""
        buffer: str = ""
        for chat in self.chat_histories:
            buffer += f"Human:{chat.get('human')}\nAI:{chat.get('ai')}\n\n"
        return buffer.strip()

    def load_memory_variables(self) -> dict[str, Any]:
        """加载记忆变量为一个字典，便于格式化到prompt中"""
        buffer_string = self.get_buffer_string()
        return {
            "chat_history": f"摘要:{self.summary}\n\n历史信息:{buffer_string}\n"
        }

    def summary_text(self, origin_summary: str, new_line: str) -> str:
        """用于将旧摘要和传入的新对话生成一个新摘要"""
        prompt = f"""你是一个强大的聊天机器人，请根据用户提供的谈话内容，总结摘要，并将其添加到先前提供的摘要中，返回一个新的摘要，除了新摘要其他任何数据都不要生成，如果用户的对话信息里有一些关键的信息，比方说姓名、爱好、性别、重要事件等等，这些全部都要包括在生成的摘要中，摘要尽可能要还原用户的对话记录。

请不要将<example>标签里的数据当成实际的数据，这里的数据只是一个示例数据，告诉你该如何生成新摘要。

<example>
当前摘要：人类会问人工智能对人工智能的看法，人工智能认为人工智能是一股向善的力量。

新的对话：
Human：为什么你认为人工智能是一股向善的力量？
AI：因为人工智能会帮助人类充分发挥潜力。

新摘要：人类会问人工智能对人工智能的看法，人工智能认为人工智能是一股向善的力量，因为它将帮助人类充分发挥潜力。
</example>

=====================以下的数据是实际需要处理的数据=====================

当前摘要：{origin_summary}

新的对话：
{new_line}

请帮用户将上面的信息生成新摘要。"""
        completion = self._client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content


# 1.创建openai客户端
client = OpenAI(base_url='https://api.xty.app/v1')
memory = ConversationSummaryBufferMemory("", [], 300)

# 2.创建一个死循环用于人机对话
while True:
    # 3.获取人类的输入
    query = input('Human: ')

    # 4.判断下输入是否为q，如果是则退出
    if query == 'q':
        break

    # 5.向openai的接口发起请求获取ai生成的内容
    memory_variables = memory.load_memory_variables()
    answer_prompt = (
        "你是一个强大的聊天机器人，请根据对应的上下文和用户提问解决问题。\n\n"
        f"{memory_variables.get('chat_history')}\n\n"
        f"用户的提问是: {query}"
    )
    response = client.chat.completions.create(
        model='gpt-4-turbo',
        messages=[
            {"role": "user", "content": answer_prompt},
        ],
        stream=True,
    )

    # 6.循环读取流式响应的内容
    print("AI: ", flush=True, end="")
    ai_content = ""
    for chunk in response:
        content = chunk.choices[0].delta.content
        if content is None:
            break
        ai_content += content
        print(content, flush=True, end="")
    print("")
    memory.save_context(query, ai_content)
