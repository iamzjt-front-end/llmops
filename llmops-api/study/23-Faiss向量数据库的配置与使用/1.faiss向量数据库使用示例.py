import dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

dotenv.load_dotenv()

embedding = OpenAIEmbeddings(model='text-embedding-3-small')

db = FAISS.load_local(
  './vector-store/', embedding, allow_dangerous_deserialization=True
)

print(db.similarity_search_with_score('我养了一只猫，叫笨笨'))
