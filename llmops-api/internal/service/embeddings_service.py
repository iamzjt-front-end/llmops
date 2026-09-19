import os
from functools import cached_property

import tiktoken
from injector import inject, singleton
from langchain_classic.embeddings import CacheBackedEmbeddings
from langchain_community.storage import RedisStore
from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings
from redis import Redis


@singleton
@inject
class EmbeddingsService:
  """文本嵌入及 Redis 缓存；首次检索或索引时才初始化模型。"""

  def __init__(self, redis: Redis):
    self._redis = redis

  @cached_property
  def store(self) -> RedisStore:
    return RedisStore(client=self._redis)

  @cached_property
  def embeddings(self) -> Embeddings:
    return OpenAIEmbeddings(
      model=os.getenv('EMBEDDING_MODEL', 'text-embedding-3-small'),
      api_key=os.getenv('EMBEDDING_API_KEY') or os.getenv('OPENAI_API_KEY'),
      base_url=os.getenv('EMBEDDING_BASE_URL') or os.getenv('OPENAI_API_BASE'),
    )

  @cached_property
  def cache_backed_embeddings(self) -> CacheBackedEmbeddings:
    return CacheBackedEmbeddings.from_bytes_store(
      self.embeddings,
      self.store,
      namespace=f'embeddings:{self.embeddings.model}',
      key_encoder='sha256',
    )

  @classmethod
  def calculate_token_count(cls, query: str) -> int:
    return len(tiktoken.get_encoding('cl100k_base').encode(query))
