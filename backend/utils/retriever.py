"""
Retrieve relevant documents from the collection based on the query.
"""
def retrieve_relevant_docs(query, model, collection, top_k=5):
    """
    Retrieve relevant documents from the collection based on the query.
    """
    query_embedding = model.encode(query).tolist()
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    return results["documents"]
