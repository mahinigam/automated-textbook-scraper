import pytest
from src.extractor.headings import HeadingExtractor

def test_detect_by_fontsize():
    # Synthetic layout data
    # Page 1: Title (size 20), Body (size 10)
    layout_data = [
        {
            "page_num": 2,
            "chars": [
                {"text": "C", "size": 20, "top": 50, "x0": 10},
                {"text": "h", "size": 20, "top": 50, "x0": 20},
                {"text": "a", "size": 20, "top": 50, "x0": 30},
                {"text": "p", "size": 20, "top": 50, "x0": 40},
                {"text": "t", "size": 20, "top": 50, "x0": 50},
                {"text": "e", "size": 20, "top": 50, "x0": 60},
                {"text": "r", "size": 20, "top": 50, "x0": 70},
                {"text": " ", "size": 20, "top": 50, "x0": 80},
                {"text": "1", "size": 20, "top": 50, "x0": 90},
                # Body text - Line 1
                {"text": "T", "size": 10, "top": 100, "x0": 10},
                {"text": "h", "size": 10, "top": 100, "x0": 20},
                {"text": "i", "size": 10, "top": 100, "x0": 30},
                {"text": "s", "size": 10, "top": 100, "x0": 40},
                # Body text - Line 2
                {"text": "i", "size": 10, "top": 120, "x0": 10},
                {"text": "s", "size": 10, "top": 120, "x0": 20},
                # Body text - Line 3
                {"text": "a", "size": 10, "top": 140, "x0": 10},
                {"text": "t", "size": 10, "top": 140, "x0": 20},
                # Body text - Line 4
                {"text": "e", "size": 10, "top": 160, "x0": 10},
                {"text": "s", "size": 10, "top": 160, "x0": 20},
            ]
        }
    ]
    
    extractor = HeadingExtractor([], layout_data)
    headings = extractor.detect_by_fontsize()
    
    assert len(headings) == 1
    assert headings[0]["text"] == "Chapter 1"
    assert headings[0]["type"] == "fontsize"

def test_detect_by_regex():
    pages_data = [
        {"page_num": 1, "text": "Chapter 1: Real Numbers\nIntroduction..."},
        {"page_num": 2, "text": "Some content..."},
        {"page_num": 3, "text": "Unit 2: Polynomials\n..."}
    ]
    
    extractor = HeadingExtractor(pages_data, [])
    headings = extractor.detect_by_regex()
    
    assert len(headings) == 2
    assert headings[0]["text"] == "Chapter 1: Real Numbers"
    assert headings[1]["text"] == "Unit 2: Polynomials"
