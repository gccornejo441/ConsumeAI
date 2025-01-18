from langchain.schema import Document
from backend.utils.splitter import splitter

def test_splitter_with_sample_documents():
    """Test the splitter function with sample documents."""
    documents = [
        Document(
            page_content="This is a sample document. It should be split into smaller chunks.",
            metadata={"source": "test"}
        )
    ]

    result = splitter(documents)

    assert result is not None
    assert len(result) > 0
    assert result[0].page_content.startswith("This is a sample document.")