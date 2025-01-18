from fastapi import FastAPI, Query
import chromadb
from sentence_transformers import SentenceTransformer
from utils.retriever import retrieve_relevant_docs

app = FastAPI()

client = chromadb.PersistentClient(path="./db/chroma_storage")

collection = client.get_or_create_collection(name="domain_docs")

model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')


@app.get("/query")
def query_consume(user_query: str = Query(...)):
    """
    Endpoint to query documents based on user input.
    """
    print(f"Received query: {user_query}")
    docs = retrieve_relevant_docs(user_query, model, collection)
    return {"query": user_query, "retrieved_docs": docs}
