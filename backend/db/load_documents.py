import os
from sentence_transformers import SentenceTransformer
import chromadb

client = chromadb.Client()
collection = client.create_collection(name="domain_docs")
model = SentenceTransformer('all-MiniLM-L6-v2')
