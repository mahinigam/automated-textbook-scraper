import pdfplumber
import logging
import json
from pathlib import Path
from typing import Dict, List, Any
from .ocr import extract_text_from_image, is_tesseract_available
from ..scraper.config import PARSED_DIR

logger = logging.getLogger(__name__)

SCANNED_TEXT_THRESHOLD = 50  # Characters per page to consider it "text-based"

class PDFParser:
    def __init__(self, pdf_path: Path, book_id: str):
        self.pdf_path = pdf_path
        self.book_id = book_id
        self.output_dir = PARSED_DIR / book_id
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.ocr_available = is_tesseract_available()

    def parse(self) -> Dict[str, Any]:
        """
        Parses the PDF, extracting text and layout.
        Applies OCR if the page appears to be scanned.
        Saves results to JSON files.
        """
        logger.info(f"Parsing PDF: {self.pdf_path}")
        
        pages_data = []
        layout_data = []
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    page_num = i + 1
                    logger.info(f"Processing page {page_num}")
                    
                    # Extract text and layout
                    text = page.extract_text() or ""
                    chars = page.chars
                    
                    is_scanned = len(text.strip()) < SCANNED_TEXT_THRESHOLD
                    ocr_applied = False
                    ocr_conf = 0.0
                    
                    if is_scanned and self.ocr_available:
                        logger.info(f"Page {page_num} appears scanned. Applying OCR...")
                        # Render page to image
                        # resolution=300 is good for OCR
                        im = page.to_image(resolution=300).original
                        text, ocr_data = extract_text_from_image(im)
                        ocr_applied = True
                        # Calculate average confidence
                        confs = [float(c) for c in ocr_data.get('conf', []) if c != '-1']
                        ocr_conf = sum(confs) / len(confs) if confs else 0.0
                    
                    page_info = {
                        "page_num": page_num,
                        "text": text,
                        "width": float(page.width),
                        "height": float(page.height),
                        "is_scanned": is_scanned,
                        "ocr_applied": ocr_applied,
                        "ocr_confidence": ocr_conf
                    }
                    
                    pages_data.append(page_info)
                    
                    # Store detailed layout info (chars) separately to avoid massive JSONs if not needed
                    # But requirements say "Store parsed pages... layout.json"
                    # We'll store chars for layout analysis
                    layout_data.append({
                        "page_num": page_num,
                        "chars": self._serialize_chars(chars)
                    })
            
            # Save results
            self._save_json(pages_data, "pages.json")
            self._save_json(layout_data, "layout.json")
            
            return {"pages": pages_data, "layout": layout_data}
            
        except Exception as e:
            logger.error(f"Failed to parse PDF {self.pdf_path}: {e}")
            return {}

    def _serialize_chars(self, chars: List[Dict]) -> List[Dict]:
        """Helper to make chars JSON serializable (decimal to float)."""
        serializable = []
        for char in chars:
            c = char.copy()
            # Convert Decimals to float
            for k, v in c.items():
                if hasattr(v, 'real'): # Check if number
                    c[k] = float(v)
            # Remove object refs
            c.pop('font', None)
            c.pop('matrix', None)
            serializable.append(c)
        return serializable

    def _save_json(self, data: Any, filename: str):
        path = self.output_dir / filename
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {path}")

def parse_pdf_wrapper(pdf_path: Path, book_id: str):
    parser = PDFParser(pdf_path, book_id)
    return parser.parse()
