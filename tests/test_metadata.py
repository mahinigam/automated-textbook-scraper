import pytest
from pathlib import Path
from src.extractor.metadata import MetadataExtractor

def test_extract_from_path():
    # Path: data/pdfs/CBSE/10/Mathematics/book.pdf
    path = Path("data/pdfs/CBSE/10/Mathematics/book.pdf")
    pages = []
    
    extractor = MetadataExtractor(path, pages)
    meta = extractor.extract()
    
    assert meta["board"] == "CBSE"
    assert meta["class"] == "10"
    assert meta["subject"] == "Mathematics"

def test_extract_from_content():
    # Path with unknown metadata
    path = Path("data/pdfs/Unknown/Unknown/Unknown/book.pdf")
    pages = [
        {"text": "Textbook for Class 10\nSubject: Mathematics\n..."},
        {"text": "Index..."},
        {"text": "Chapter 1..."}
    ]
    
    extractor = MetadataExtractor(path, pages)
    meta = extractor.extract()
    
    assert meta["class"] == "10"
    assert meta["subject"] == "Mathematics"
