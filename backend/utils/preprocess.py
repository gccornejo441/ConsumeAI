import spacy

from langchain.schema import Document

nlp = spacy.load("en_core_web_sm")

def preprocess_with_spacy(documents) -> list:
    """Use spaCy to preprocess and split documents into sentences."""
    split_docs = []

    for doc in documents:
        content = doc.page_content if isinstance(
            doc, Document) else doc["page_content"]
        metadata = doc.metadata if isinstance(
            doc, Document) else doc["metadata"]

        spacy_doc = nlp(content)
        sentences = [sent.text.strip() for sent in spacy_doc.sents]

        for sentence in sentences:
            split_docs.append(
                Document(page_content=sentence, metadata=metadata))

    return split_docs
