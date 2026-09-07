import os

import dotenv
import numpy as np
from langchain_community.embeddings import OpenAIEmbeddings
from numpy.linalg import norm

dotenv.load_dotenv()


def cosine_similarity(vec1: list, vec2: list) -> float:
  """计算传入的两个向量的余弦相似度"""
  # 1.计算两个向量的点积
  dot_product = np.dot(vec1, vec2)

  # 2.计算向量的长度
  vec1_norm = norm(vec1)
  vec2_norm = norm(vec2)

  # 3.计算余弦相似度
  return dot_product / (vec1_norm * vec2_norm)


# 1.创建文本嵌入模型
embedding = OpenAIEmbeddings(
  model='embedding-3',
  api_key=os.getenv('GLM_API_KEY'),
  base_url=os.getenv('GLM_API_BASE'),
)

# 2.嵌入文本
query_vector = embedding.embed_query('你好，我是zjt，我喜欢摄影')

print(query_vector)
print(len(query_vector))

# 3.嵌入文档列表/字符串列表
documents_vector = embedding.embed_documents(
  [
    '我叫zjt，我喜欢摄影',
    '我喜欢摄影，我的名字叫zjt',
    '你好',
  ]
)

print(len(documents_vector))

# 4.计算余弦相似度
print(
  f'向量1和向量2的相似度: {cosine_similarity(documents_vector[0], documents_vector[1])})'
)
print(
  f'向量1和向量3的相似度: {cosine_similarity(documents_vector[0], documents_vector[2])})'
)
