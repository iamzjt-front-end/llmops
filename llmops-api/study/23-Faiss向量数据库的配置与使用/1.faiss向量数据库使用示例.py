import os

import dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

dotenv.load_dotenv()

embedding = OpenAIEmbeddings(
  model='embedding-3',
  api_key=os.getenv('GLM_API_KEY'),
  base_url=os.getenv('GLM_API_BASE'),
)

db = FAISS.load_local(
  './vector-store/', embedding, allow_dangerous_deserialization=True
)

print(db.similarity_search_with_score('我养了一只猫，叫笨笨'))
