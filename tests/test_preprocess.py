import pytest
from langchain.schema import Document
from backend.utils.preprocess import preprocess_with_spacy

def test_preprocess_with_spacy_documents():
    """Test preprocess_with_spacy with Document objects."""
    documents = [
        Document(
            page_content="This is the first sentence. Here is the second sentence.",
            metadata={"source": "test1"}
        ),
        Document(
            page_content="Another document here. With two more sentences.",
            metadata={"source": "test2"}
        )
    ]

    result = preprocess_with_spacy(documents)

    assert len(result) == 4 
    assert result[0].page_content == "This is the first sentence."
    assert result[1].page_content == "Here is the second sentence."
    assert result[2].metadata["source"] == "test2"

def test_preprocess_with_spacy_dicts():
    """Test preprocess_with_spacy with dictionaries."""
    documents = [
        {
            "page_content": "A single document with multiple sentences. Here's another sentence.",
            "metadata": {"source": "dict_test"}
        }
    ]

    result = preprocess_with_spacy(documents)

    assert len(result) == 2  
    assert result[0].page_content == "A single document with multiple sentences."
    assert result[1].page_content == "Here's another sentence."
    assert result[0].metadata["source"] == "dict_test"
