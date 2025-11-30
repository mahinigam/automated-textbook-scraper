import pytest
from unittest.mock import patch, MagicMock
from src.scraper.discover import NCERTScraper

@patch('src.scraper.discover.requests.get')
def test_discover_books_fallback(mock_get):
    # Mock response to return empty HTML so it triggers fallback
    mock_response = MagicMock()
    mock_response.text = "<html></html>"
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    scraper = NCERTScraper()
    books = scraper.discover_books()
    
    assert len(books) > 0
    assert books[0]["board"] == "CBSE"
    assert "book_code" in books[0]

def test_generate_chapter_urls():
    scraper = NCERTScraper()
    urls = scraper.generate_chapter_urls("lemh1", num_chapters=5)
    
    assert len(urls) == 6 # 5 chapters + prelims
    assert "lemh101.pdf" in urls[0]
