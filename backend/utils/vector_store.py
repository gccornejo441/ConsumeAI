import os
from langchain_community.vectorstores import Chroma
from langchain_community.vectorstores.utils import filter_complex_metadata
from backend.utils.embedding import embedding_model


PERSIST_DIRECTORY = ".backend/db/chroma_storage"


def create_vector_store(documents):
    """
    Create or update a persistent Chroma vector store using HuggingFace embeddings.
    """
    os.makedirs(PERSIST_DIRECTORY, exist_ok=True)

    processed_documents = filter_complex_metadata(documents)
    embeddings = embedding_model()

    vector_store = None
    if os.path.exists(PERSIST_DIRECTORY):
        vector_store = Chroma(
            persist_directory=PERSIST_DIRECTORY,
            embedding_function=embeddings
        )
    else:
        vector_store = Chroma.from_documents(
            processed_documents,
            embeddings,
            persist_directory=PERSIST_DIRECTORY
        )

    vector_store.add_documents(processed_documents)
    vector_store.persist()

    return vector_store
