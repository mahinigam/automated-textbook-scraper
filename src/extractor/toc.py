import re
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class ToCExtractor:
    def __init__(self, pages_data: List[Dict]):
        self.pages = pages_data

    def extract(self) -> List[Dict]:
        """
        Strategy C: Extract chapters from Table of Contents.
        """
        logger.info("Running Strategy C: ToC Extraction")
        toc_pages = self._find_toc_pages()
        if not toc_pages:
            logger.warning("No ToC pages found.")
            return []
            
        chapters = []
        
        # Regex for "Chapter Name ....... 12"
        # Handles dots (with optional spaces), and trailing page number
        # Matches: "Chapter 1 ... 5", "Chapter 1 . . . 5", "Chapter 1       5"
        pattern = r"^(.*?)(?:(?:\. ?){2,}|\s{2,})(\d+)$"
        
        for page in toc_pages:
            text = page.get('text', '')
            logger.info(f"Scanning ToC page {page.get('page_num')} content: {text[:50]}...")
            lines = text.split('\n')
            
            for line in lines:
                line = line.strip()
                match = re.match(pattern, line)
                if match:
                    title = match.group(1).strip()
                    page_num = int(match.group(2))
                    logger.info(f"ToC Match: {title} -> {page_num}")
                    
                    # Filter out noise
                    if len(title) < 3 or page_num > 1000:
                        continue
                        
                    chapters.append({
                        "chapter_name": title,
                        "start_page": page_num,
                        "type": "toc",
                        "confidence": 0.9
                    })
                    
        return chapters

    def _find_toc_pages(self) -> List[Dict]:
        """
        Identifies pages that are likely part of the Table of Contents.
        Checks first 15 pages for keywords.
        """
        candidates = []
        keywords = ["content", "contents", "table of contents", "index", "visay suchi"]
        
        # Only check first 15 pages
        for i, page in enumerate(self.pages[:15]):
            text = page.get('text', '').lower()
            if any(k in text for k in keywords):
                candidates.append(page)
                
        return candidates
