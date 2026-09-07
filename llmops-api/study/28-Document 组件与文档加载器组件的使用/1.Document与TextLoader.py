from langchain_community.document_loaders import TextLoader

# 1.构建加载器
loader = TextLoader("./电商产品数据.txt", encoding="utf-8")

# 2.加载数据
documents = loader.load()

print(documents)
print(len(documents))
print(documents[0].metadata)
