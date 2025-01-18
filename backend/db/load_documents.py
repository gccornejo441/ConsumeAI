import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader

def load_documents(directory):
    """Load PDF and TXT documents from the specified directory."""
    documents = []
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(filepath)
        elif filename.endswith(".txt"):
            loader = TextLoader(filepath)
        else:
            print(f"Skipping unsupported file type: {filename}")
            continue
        documents.extend(loader.load())
    return documents
