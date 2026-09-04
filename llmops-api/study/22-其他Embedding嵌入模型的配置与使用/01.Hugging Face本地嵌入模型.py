from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
  model_name='sentence-transformers/all-MiniLM-L12-v2', cache_folder='./embeddings/'
)

query_vector = embeddings.embed_query('你好，我是zjt，我喜欢打篮球游泳')

print(query_vector)
print(len(query_vector))
