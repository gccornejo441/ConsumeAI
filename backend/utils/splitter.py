from langchain.text_splitter import RecursiveCharacterTextSplitter

from backend.utils.preprocess import preprocess_with_spacy

def splitter(documents) -> list:
    """
    Split documents into smaller chunks using RecursiveCharacterTextSplitter.
    """
    preprocessed_docs = preprocess_with_spacy(documents)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, chunk_overlap=50)
    split_docs = text_splitter.split_documents(preprocessed_docs)

    return split_docs