#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/7/2 8:32
@Author  : thezehui@gmail.com
@File    : 1.自定义加载器使用技巧.py
"""
from typing import Iterator, AsyncIterator

from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document


class CustomDocumentLoader(BaseLoader):
    """自定义文档加载器，将文本文件的每一行都解析成Document"""

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    def lazy_load(self) -> Iterator[Document]:
        # 1.读取对应的文件
        with open(self.file_path, encoding="utf-8") as f:
            line_number = 0
            # 2.提取文件的每一行
            for line in f:
                # 3.将每一行生成一个Document实例并通过yield返回
                yield Document(
                    page_content=line,
                    metadata={"score": self.file_path, "line_number": line_number}
                )
                line_number += 1

    async def alazy_load(self) -> AsyncIterator[Document]:
        import aiofiles
        async with aiofiles.open(self.file_path, encoding="utf-8") as f:
            line_number = 0
            async for line in f:
                yield Document(
                    page_content=line,
                    metadata={"score": self.file_path, "line_number": line_number}
                )
                line_number += 1


loader = CustomDocumentLoader("./喵喵.txt")
documents = loader.load()

print(documents)
print(len(documents))
print(documents[0].metadata)
