import os

from flask import request
from openai import OpenAI


class AppHandler:
    """应用控制器"""

    def completion(self):
        """聊天接口"""
        # 1.提取从接口中获取的输入，POST
        query = request.json.get("query")

        # 2.构建OpenAI客户端，并发起请求
        client = OpenAI(base_url=os.getenv("OPENAI_API_BASE"))

        # 3.得到请求响应，然后将OpenAI的响应传递给前端
        completion = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=[
                {
                    "role": "system",
                    "content": "你是OpenAI开发的聊天机器人，请根据用户的输入回复对应的信息",
                },
                {
                    "role": "user",
                    "content": query,
                },
            ],
        )

        content = completion.choices[0].message.content
        return content

    def ping(self):
        return {"ping": "pong"}
