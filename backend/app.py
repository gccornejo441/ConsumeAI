from fastapi import FastAPI, Query
import chromadb
from sentence_transformers import SentenceTransformer

from utils.retriever import retrieve_relevant_docs

app = FastAPI()

client = chromadb.Client()
collection = client.create_collection(name="domain_docs")

model = SentenceTransformer('all-MiniLM-L6-v2')


@app.get("/query")
def query_consume(user_query: str = Query(...)):
    docs = retrieve_relevant_docs(user_query, model, collection)
    return {"query": user_query, "retrieved_docs": docs}
