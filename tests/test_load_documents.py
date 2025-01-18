import os
from fpdf import FPDF
import pytest
from unittest.mock import patch, MagicMock
from backend.db.load_documents import load_documents
from tempfile import TemporaryDirectory


def test_load_documents_with_mocked_files():
    """Unit test for load_documents with mocked files and loaders."""
    mocked_files = ["file1.pdf", "file2.txt", "unsupported.docx"]
    
    with patch("os.listdir", return_value=mocked_files), \
         patch("os.path.join", side_effect=lambda directory, filename: f"{directory}/{filename}"):
        
        mock_pdf_loader = MagicMock()
        mock_pdf_loader.load.return_value = [
            {"page_content": "PDF content", "metadata": {}}
        ]

        mock_text_loader = MagicMock()
        mock_text_loader.load.return_value = [
            {"page_content": "Text content", "metadata": {}}
        ]

        with patch("backend.db.load_documents.PyPDFLoader", return_value=mock_pdf_loader), \
             patch("backend.db.load_documents.TextLoader", return_value=mock_text_loader):

            documents = load_documents("./mocked_dir")

            assert len(documents) == 2
            assert documents[0]["page_content"] == "PDF content"
            assert documents[1]["page_content"] == "Text content"


def create_mock_pdf(file_path, content="Mock PDF content"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=content, ln=True, align="C")
    pdf.output(file_path)

@pytest.mark.integration
def test_load_documents_integration():
    """Integration test for load_documents using temporary files."""
    with TemporaryDirectory() as temp_dir:
        pdf_file = os.path.join(temp_dir, "test.pdf")
        txt_file = os.path.join(temp_dir, "test.txt")
        unsupported_file = os.path.join(temp_dir, "unsupported.docx")

        with open(txt_file, "w") as f:
            f.write("This is a text file.")

        create_mock_pdf(pdf_file, "This is a valid mock PDF file.")

        with open(unsupported_file, "w") as f:
            f.write("This file should be skipped.")

        documents = load_documents(temp_dir)

        assert len(documents) == 2
        assert any(doc.page_content.startswith("This is a text file") for doc in documents)
        assert any("valid mock PDF" in doc.page_content for doc in documents)
