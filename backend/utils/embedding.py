from langchain_community.embeddings import HuggingFaceEmbeddings

def embedding_model():
    """Return the HuggingFaceEmbeddings model."""
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
