import re
import statistics
import logging
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)

class HeadingExtractor:
    def __init__(self, pages_data: List[Dict], layout_data: List[Dict]):
        self.pages = pages_data
        self.layout = layout_data
        self.headings = []

    def detect_by_fontsize(self) -> List[Dict]:
        """
        Strategy A: Detect headings based on font size.
        """
        logger.info("Running Strategy A: Font Size Detection")
        candidates = []
        all_sizes = []
        
        # First pass: Collect all line font sizes to compute stats
        # We need to reconstruct lines from chars first
        page_lines = {} # page_num -> list of (text, avg_size, top)
        
        for page_layout in self.layout:
            page_num = page_layout['page_num']
            chars = page_layout['chars']
            if not chars:
                continue
                
            lines = self._group_chars_into_lines(chars)
            page_lines[page_num] = lines
            
            for _, size, _ in lines:
                all_sizes.append(size)
                
        if not all_sizes:
            return []
            
        mean_size = statistics.mean(all_sizes)
        try:
            std_dev = statistics.stdev(all_sizes)
        except statistics.StatisticsError:
            std_dev = 0
            
        threshold = mean_size + std_dev
        logger.info(f"Font size stats: Mean={mean_size:.2f}, Std={std_dev:.2f}, Threshold={threshold:.2f}")
        
        # Second pass: Identify headings
        for page_num, lines in page_lines.items():
            if page_num == 1: # Skip title page
                continue
            for text, size, top in lines:
                if size >= threshold:
                    # Apply filters
                    if len(text) > 80:
                        continue
                    if any(x in text.lower() for x in ["summary", "review", "index", "bibliography"]):
                        continue
                        
                    candidates.append({
                        "page_num": page_num,
                        "text": text.strip(),
                        "type": "fontsize",
                        "score": (size - mean_size) / (std_dev if std_dev > 0 else 1)
                    })
                    
        return candidates

    def detect_by_regex(self) -> List[Dict]:
        """
        Strategy B: Detect headings based on regex patterns.
        """
        logger.info("Running Strategy B: Regex Detection")
        candidates = []
        
        patterns = [
            r"Chapter\s*\d+",
            r"CHAPTER\s+\d+",
            r"Unit\s*\d+",
            r"Lesson\s*\d+",
            r"अध्याय\s*\d+",   # Hindi
            r"பாடம்\s*\d+",    # Tamil
            r"ಅಧ್ಯಾಯ\s*\d+"     # Kannada
        ]
        
        for page in self.pages:
            text = page.get('text', '')
            if not text:
                continue
                
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                # Ignore ToC lines (e.g. "Chapter 1 ... 5")
                if ".." in line:
                    continue
                    
                for pattern in patterns:
                    if re.match(pattern, line, re.IGNORECASE):
                        candidates.append({
                            "page_num": page['page_num'],
                            "text": line,
                            "type": "regex",
                            "score": 1.0
                        })
                        break # Match first pattern only per line
                        
        return candidates

    def _group_chars_into_lines(self, chars: List[Dict]) -> List[Tuple[str, float, float]]:
        """
        Groups characters into lines based on 'top' coordinate.
        Returns list of (text, avg_size, top).
        """
        # Sort by top, then x0
        chars.sort(key=lambda c: (c['top'], c['x0']))
        
        lines = []
        current_line_chars = []
        current_top = -1
        
        TOLERANCE = 3 # pixels
        
        for char in chars:
            if current_top == -1:
                current_top = char['top']
                current_line_chars.append(char)
            elif abs(char['top'] - current_top) <= TOLERANCE:
                current_line_chars.append(char)
            else:
                # Process completed line
                if current_line_chars:
                    lines.append(self._process_line(current_line_chars))
                current_line_chars = [char]
                current_top = char['top']
                
        if current_line_chars:
            lines.append(self._process_line(current_line_chars))
            
        return lines

    def _process_line(self, chars: List[Dict]) -> Tuple[str, float, float]:
        text = "".join([c['text'] for c in chars])
        sizes = [c['size'] for c in chars]
        avg_size = sum(sizes) / len(sizes) if sizes else 0
        top = chars[0]['top']
        return text, avg_size, top
