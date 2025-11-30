import pytest
from unittest.mock import patch, MagicMock
from src.parser.pdf_parser import PDFParser
from pathlib import Path

@patch('src.parser.pdf_parser.pdfplumber.open')
def test_parse_pdf_text(mock_open):
    # Mock PDF object
    mock_pdf = MagicMock()
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Sample text content that is definitely longer than fifty characters to ensure it is not detected as scanned."
    mock_page.chars = [{"text": "S", "size": 10}]
    mock_page.width = 100
    mock_page.height = 100
    
    mock_pdf.pages = [mock_page]
    mock_open.return_value.__enter__.return_value = mock_pdf
    
    parser = PDFParser(Path("dummy.pdf"), "book1")
    result = parser.parse()
    
    assert len(result["pages"]) == 1
    assert result["pages"][0]["text"] == "Sample text content that is definitely longer than fifty characters to ensure it is not detected as scanned."
    assert result["pages"][0]["is_scanned"] == False

@patch('src.parser.pdf_parser.pdfplumber.open')
@patch('src.parser.pdf_parser.extract_text_from_image')
def test_parse_pdf_scanned(mock_ocr, mock_open):
    # Mock scanned page (empty text)
    mock_pdf = MagicMock()
    mock_page = MagicMock()
    mock_page.extract_text.return_value = ""
    mock_page.chars = []
    mock_page.width = 100
    mock_page.height = 100
    
    mock_pdf.pages = [mock_page]
    mock_open.return_value.__enter__.return_value = mock_pdf
    
    # Mock OCR result
    mock_ocr.return_value = ("OCR Text", {"conf": [90]})
    
    parser = PDFParser(Path("dummy.pdf"), "book1")
    # Force OCR available
    parser.ocr_available = True
    
    result = parser.parse()
    
    assert len(result["pages"]) == 1
    assert result["pages"][0]["is_scanned"] == True
    assert result["pages"][0]["ocr_applied"] == True
    assert result["pages"][0]["text"] == "OCR Text"
