import re
import logging
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)

class MetadataExtractor:
    def __init__(self, file_path: Path, pages_data: List[Dict]):
        self.file_path = file_path
        self.pages = pages_data

    def extract(self) -> Dict[str, str]:
        """
        Extracts metadata from file path and content.
        """
        metadata = {
            "board": "Unknown",
            "class": "Unknown",
            "subject": "Unknown",
            "title": "Unknown"
        }
        
        # 1. Extract from Path
        # Expected: .../data/pdfs/{board}/{class}/{subject}/{filename}.pdf
        parts = self.file_path.parts
        if "pdfs" in parts:
            idx = parts.index("pdfs")
            if len(parts) > idx + 3:
                metadata["board"] = parts[idx + 1]
                metadata["class"] = parts[idx + 2]
                metadata["subject"] = self._normalize_subject(parts[idx + 3])
                
        # 2. Extract from Content (Title Page / First 3 Pages)
        # If path metadata is unknown, try to find it in the text
        if self.pages:
            # Check first 3 pages
            text_content = "\n".join([p.get('text', '') for p in self.pages[:3]])
            
            if metadata["class"] == "Unknown":
                # Look for "Class X" or "Class 10"
                class_match = re.search(r"Class\s+([VIX0-9]+)", text_content, re.IGNORECASE)
                if class_match:
                    metadata["class"] = class_match.group(1)

            if metadata["subject"] == "Unknown":
                # Look for common subjects
                subjects = ["Mathematics", "Science", "Social Science", "English", "Physics", "Chemistry", "Biology", "History", "Geography"]
                for subj in subjects:
                    if re.search(r"\b" + re.escape(subj) + r"\b", text_content, re.IGNORECASE):
                        metadata["subject"] = subj
                        break
            
            # Try to extract title if it looks like a filename
            if metadata["title"] == "Unknown" or metadata["title"] == self.file_path.stem:
                # Heuristic: First line of first page might be title if it's short
                first_line = self.pages[0].get('text', '').split('\n')[0].strip()
                if 3 < len(first_line) < 50:
                     metadata["title"] = first_line.title()

        if metadata["title"] == "Unknown":
            metadata["title"] = self.file_path.stem
            
        return metadata

    def _normalize_subject(self, subject: str) -> str:
        """Normalizes subject names."""
        s = subject.lower()
        if "math" in s:
            return "Mathematics"
        if "eng" in s:
            return "English"
        if "soc" in s or "social" in s:
            return "Social Science"
        if "sci" in s and "social" not in s:
            return "Science"
        return subject.title()
