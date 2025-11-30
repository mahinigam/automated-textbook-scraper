import requests
import logging
import re
import time
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from urllib.parse import urljoin
from .config import NCERT_TEXTBOOK_URL, NCERT_BASE_URL, HEADERS, REQUEST_DELAY

logger = logging.getLogger(__name__)

class NCERTScraper:
    def __init__(self):
        self.base_url = NCERT_TEXTBOOK_URL
        self.books = []

    def fetch_page(self, url: str) -> Optional[str]:
        try:
            time.sleep(REQUEST_DELAY)
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None

    def discover_books(self) -> List[Dict]:
        """
        Discovers books by parsing the NCERT textbook page.
        Since the page uses dynamic JS, we'll try to extract the data from scripts
        or use a fallback list of known codes for demonstration.
        """
        logger.info("Starting discovery on NCERT...")
        html = self.fetch_page(self.base_url)
        if not html:
            return []

        # Strategy 1: Look for JS arrays defining the books
        # Often found in scripts like: s[1][1] = "Book Name";
        books = self._extract_from_js(html)
        
        if not books:
            logger.warning("Could not extract books from JS. Using fallback known list.")
            books = self._get_fallback_books()

        logger.info(f"Discovered {len(books)} books.")
        return books

    def _extract_from_js(self, html: str) -> List[Dict]:
        """
        Attempts to extract book codes and titles from embedded JS.
        """
        books = []
        # This is a heuristic. Real parsing would require a JS engine or complex regex.
        # We look for patterns like: new Option("Book Title", "BookCode")
        # or specific array assignments.
        
        # Regex to find option creation: new Option("Text", "Value")
        # This is common in older PHP/JS sites.
        pattern = r'new Option\s*\(\s*"([^"]+)"\s*,\s*"([^"]+)"\s*\)'
        matches = re.findall(pattern, html)
        
        for name, code in matches:
            if code and len(code) > 2: # Filter out dummy options
                # Try to guess class/subject from name or context
                # For now, we just store the code and name
                books.append({
                    "title": name,
                    "book_code": code,
                    "board": "CBSE", # NCERT is primarily CBSE
                    "class": "Unknown", # Would need more context
                    "subject": "Unknown"
                })
        
        return books

    def _get_fallback_books(self) -> List[Dict]:
        """
        Returns a list of known book codes for demonstration purposes.
        """
        return [
            # Class 10
            {"title": "Mathematics", "book_code": "jemh1", "class": "10", "subject": "Mathematics", "board": "CBSE"},
            {"title": "Science", "book_code": "jesc1", "class": "10", "subject": "Science", "board": "CBSE"},
            {"title": "India and the Contemporary World-II", "book_code": "jess3", "class": "10", "subject": "Social Science", "board": "CBSE"},
            # Class 12
            {"title": "Mathematics Part-I", "book_code": "lemh1", "class": "12", "subject": "Mathematics", "board": "CBSE"},
            {"title": "Physics Part-I", "book_code": "leph1", "class": "12", "subject": "Physics", "board": "CBSE"},
        ]

    def generate_chapter_urls(self, book_code: str, num_chapters: int = 20) -> List[str]:
        """
        Generates PDF URLs for a given book code.
        NCERT format: https://ncert.nic.in/textbook/pdf/{book_code}{chapter}.pdf
        """
        urls = []
        # Try chapters 1 to N. We don't know N, so we can try until 404 or use a fixed limit.
        # For the pipeline, we'll generate a list and the fetcher will handle 404s.
        for i in range(1, num_chapters + 1):
            chap_num = f"{i:02d}" # 01, 02, ...
            url = f"https://ncert.nic.in/textbook/pdf/{book_code}{chap_num}.pdf"
            urls.append(url)
        
        # Also add "ps" (prelims) and "an" (answers) sometimes?
        # Usually prelims is {book_code}ps.pdf
        urls.append(f"https://ncert.nic.in/textbook/pdf/{book_code}ps.pdf")
        return urls

class CISCEScraper:
    def __init__(self):
        self.base_url = "https://cisce.org/publications/"
        # CISCE doesn't have a direct textbook repo like NCERT.
        # They list prescribed texts which are often from private publishers.
        # However, for the purpose of this pipeline, we will simulate discovery
        # or point to sample open resources if available.
        
    def discover_books(self) -> List[Dict]:
        """
        Discovers ICSE books. 
        Since there is no central repo, we return a list of known open resources or placeholders.
        """
        logger.info("Starting discovery on CISCE...")
        # Simulating discovery
        books = [
            {
                "title": "Mathematics Class 10",
                "book_code": "icse_math_10",
                "class": "10",
                "subject": "Mathematics",
                "board": "ICSE",
                "url": "https://example.com/icse_math_10.pdf" # Placeholder
            },
            {
                "title": "Physics Class 10",
                "book_code": "icse_phy_10",
                "class": "10",
                "subject": "Physics",
                "board": "ICSE",
                "url": "https://example.com/icse_phy_10.pdf" # Placeholder
            }
        ]
        return books

    def generate_chapter_urls(self, book_code: str) -> List[str]:
        # For ICSE simulation, we might just return the single book URL
        # or simulate chapter URLs
        return [f"https://example.com/{book_code}.pdf"]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scraper = NCERTScraper()
    books = scraper.discover_books()
    for book in books:
        print(book)
