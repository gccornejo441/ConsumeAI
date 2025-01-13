import os
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb

client = chromadb.PersistentClient(path="./db/chroma_storage")

print(
    f"Debug: ChromaDB will store data in {os.path.abspath('./db/chroma_storage')}")

collection = client.get_or_create_collection(name="domain_docs")

model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

DOCUMENTS_DIR = "./db/documents"


def load_and_store_documents():
    print("Debug: Starting document load...")
    print(f"Debug: DOCUMENTS_DIR path is {os.path.abspath(DOCUMENTS_DIR)}")
    print(f"Debug: Files in DOCUMENTS_DIR: {os.listdir(DOCUMENTS_DIR)}")

    try:
        all_docs = collection.get(include=["documents"])
        num_docs = len(all_docs["documents"])
        if num_docs > 0:
            collection.delete(where={"document": {"$exists": True}})
            print(
                f"Debug: Cleared {num_docs} existing documents in the collection.")
        else:
            print("Debug: No documents to delete.")
    except Exception as e:
        print(f"Error while clearing documents: {e}")

    doc_id = 1
    for filename in os.listdir(DOCUMENTS_DIR):
        if filename.endswith(".txt"):
            filepath = os.path.join(DOCUMENTS_DIR, filename)
            print(f"Debug: Processing file {filename}")
            try:
                with open(filepath, "r", encoding="utf-8") as file:
                    context = file.read()
                    embedding = model.encode(context).tolist()
                    collection.add(
                        ids=[f"doc_{doc_id}"],
                        embeddings=[embedding],
                        documents=[context],
                    )
                    print(
                        f"Debug: Added document ID doc_{doc_id} with embedding {embedding[:5]}...")
                    doc_id += 1
            except Exception as e:
                print(f"Error processing file {filename}: {e}")

    print(f"Total documents in collection: {collection.count()}")


if __name__ == "__main__":
    load_and_store_documents()
