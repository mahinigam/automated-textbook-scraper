import logging
import pytesseract
from PIL import Image
from typing import Tuple, Dict

logger = logging.getLogger(__name__)

def extract_text_from_image(image: Image.Image, lang: str = 'eng') -> Tuple[str, Dict]:
    """
    Extracts text from a PIL Image using Tesseract OCR.
    
    Args:
        image: PIL Image object.
        lang: Language code (default 'eng').
        
    Returns:
        Tuple containing:
        - Extracted text string.
        - Dictionary with detailed data (conf, left, top, width, height, text).
    """
    try:
        # Get raw text
        text = pytesseract.image_to_string(image, lang=lang)
        
        # Get detailed data (bounding boxes, confidence)
        data = pytesseract.image_to_data(image, lang=lang, output_type=pytesseract.Output.DICT)
        
        return text, data
        
    except pytesseract.TesseractNotFoundError:
        logger.error("Tesseract not found. Please install Tesseract OCR.")
        return "", {}
    except Exception as e:
        logger.error(f"OCR failed: {e}")
        return "", {}

def is_tesseract_available() -> bool:
    """Checks if Tesseract is available."""
    try:
        pytesseract.get_tesseract_version()
        return True
    except pytesseract.TesseractNotFoundError:
        return False
