from langchain_community.document_loaders import (
    UnstructuredPowerPointLoader,
)

# excel_loader = UnstructuredExcelLoader("./员工考勤表.xlsx", mode="elements")
# excel_documents = excel_loader.load()

# word_loader = UnstructuredWordDocumentLoader("./喵喵.docx")
# documents = word_loader.load()

ppt_loader = UnstructuredPowerPointLoader("./章节介绍.pptx")
documents = ppt_loader.load()

print(documents)
print(len(documents))
print(documents[0].metadata)
