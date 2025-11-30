import json
import csv
import logging
from pathlib import Path
from typing import Dict, List, Any
from .scraper.config import OUTPUT_DIR

logger = logging.getLogger(__name__)

class DataExporter:
    def __init__(self, book_id: str, output_dir: Path = OUTPUT_DIR):
        self.book_id = book_id
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_json(self, metadata: Dict, chapters: List[Dict]):
        """
        Exports data to JSON.
        """
        data = {
            "book_id": self.book_id,
            "metadata": metadata,
            "chapters": chapters
        }
        
        filepath = self.output_dir / f"{self.book_id}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Exported JSON to {filepath}")

    def export_csv(self, metadata: Dict, chapters: List[Dict]):
        """
        Exports chapters to CSV.
        """
        filepath = self.output_dir / f"{self.book_id}.csv"
        
        fieldnames = ["book_id", "board", "class", "subject", "chapter_no", "chapter_name", "start_page", "end_page"]
        
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for ch in chapters:
                row = {
                    "book_id": self.book_id,
                    "board": metadata.get("board", ""),
                    "class": metadata.get("class", ""),
                    "subject": metadata.get("subject", ""),
                    "chapter_no": ch.get("chapter_no"),
                    "chapter_name": ch.get("chapter_name"),
                    "start_page": ch.get("start_page"),
                    "end_page": ch.get("end_page")
                }
                writer.writerow(row)
        logger.info(f"Exported CSV to {filepath}")

    def append_to_master_csv(self, metadata: Dict, chapters: List[Dict]):
        """
        Appends to master CSV.
        """
        filepath = self.output_dir / "all_books.csv"
        file_exists = filepath.exists()
        
        fieldnames = ["book_id", "board", "class", "subject", "chapter_no", "chapter_name", "start_page", "end_page"]
        
        with open(filepath, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            
            for ch in chapters:
                row = {
                    "book_id": self.book_id,
                    "board": metadata.get("board", ""),
                    "class": metadata.get("class", ""),
                    "subject": metadata.get("subject", ""),
                    "chapter_no": ch.get("chapter_no"),
                    "chapter_name": ch.get("chapter_name"),
                    "start_page": ch.get("start_page"),
                    "end_page": ch.get("end_page")
                }
                writer.writerow(row)
        logger.info(f"Appended to master CSV: {filepath}")

    def append_to_master_json(self, metadata: Dict, chapters: List[Dict]):
        """
        Appends to master JSON dataset (all_books.json).
        """
        filepath = self.output_dir / "all_books.json"
        
        all_data = []
        if filepath.exists():
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    all_data = json.load(f)
            except json.JSONDecodeError:
                logger.warning(f"Could not decode {filepath}, starting fresh.")
        
        # Check if book already exists, remove it to update
        all_data = [b for b in all_data if b.get("book_id") != self.book_id]
        
        new_entry = {
            "book_id": self.book_id,
            "metadata": metadata,
            "chapters": chapters
        }
        all_data.append(new_entry)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Updated master JSON: {filepath}")

    def update_metadata_index(self, metadata: Dict):
        """
        Updates the metadata index at data/metadata/index.json.
        """
        from .scraper.config import METADATA_DIR
        filepath = METADATA_DIR / "index.json"
        
        index_data = []
        if filepath.exists():
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    index_data = json.load(f)
            except json.JSONDecodeError:
                pass
                
        # Update or add
        # We use book_id as key if available, or title
        # metadata should have 'book_id' ideally, but it's passed separately in init
        # Let's inject book_id into metadata for storage
        meta_to_store = metadata.copy()
        meta_to_store["book_id"] = self.book_id
        
        # Remove existing entry for this book
        index_data = [item for item in index_data if item.get("book_id") != self.book_id]
        index_data.append(meta_to_store)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Updated metadata index: {filepath}")
