import atexit
import os
from functools import cached_property

import weaviate
from injector import inject, singleton
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_weaviate import WeaviateVectorStore
from weaviate import WeaviateClient
from weaviate.collections import Collection

from .embeddings_service import EmbeddingsService

COLLECTION_NAME = 'Dataset'


@singleton
@inject
class VectorDatabaseService:
  """向量数据库服务，首次访问时连接并复用客户端。"""

  def __init__(self, embeddings_service: EmbeddingsService):
    self.embeddings_service = embeddings_service

  @cached_property
  def client(self) -> WeaviateClient:
    client = weaviate.connect_to_local(
      host=os.getenv('WEAVIATE_HOST', 'localhost'),
      port=int(os.getenv('WEAVIATE_PORT', '8080')),
      grpc_port=int(os.getenv('WEAVIATE_GRPC_PORT', '50051')),
    )
    atexit.register(client.close)
    return client

  @cached_property
  def vector_store(self) -> WeaviateVectorStore:
    return WeaviateVectorStore(
      client=self.client,
      index_name=COLLECTION_NAME,
      text_key='text',
      embedding=self.embeddings_service.cache_backed_embeddings,
    )

  def get_retriever(self) -> VectorStoreRetriever:
    return self.vector_store.as_retriever()

  @classmethod
  def combine_documents(cls, documents: list[Document]) -> str:
    return '\n\n'.join(document.page_content for document in documents)

  @property
  def collection(self) -> Collection:
    return self.client.collections.get(COLLECTION_NAME)
