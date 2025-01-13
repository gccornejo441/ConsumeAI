def retrieve_relevant_docs(query, model, collection, top_k=20, threshold=1.0):
    """
    Retrieve relevant documents from the collection based on the query
    with a specified similarity threshold.
    Returns a dictionary with the query and the retrieved documents.
    """
    query_embedding = model.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "distances"]
    )

    print(f"Query: {query}")
    print(f"All distances: {results['distances'][0]}")

    all_docs = collection.get(include=["documents", "embeddings"])
    print(f"Total documents: {len(all_docs['documents'])}")

    retrieved_docs = []

    if results and "documents" in results and "distances" in results:
        for doc, score in zip(results["documents"][0], results["distances"][0]):
            print(f"Document: {doc[:50]}... | Distance Score: {score}")
            if score <= threshold:
                retrieved_docs.append({"document": doc, "score": score})

    if not retrieved_docs:
        retrieved_docs.append({"message": "No relevant documents found."})

    return {
        "query": query,
        "retrieved_docs": retrieved_docs
    }
