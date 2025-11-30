import logging
from pathlib import Path
from typing import Optional, Dict

from .scraper.discover import NCERTScraper, CISCEScraper
from .scraper.fetch_pdfs import download_pdf
from .scraper.config import PDF_DIR
from .parser.pdf_parser import PDFParser
from .extractor.headings import HeadingExtractor
from .extractor.toc import ToCExtractor
from .extractor.merger import ChapterMerger
from .extractor.metadata import MetadataExtractor
from .exporter import DataExporter

logger = logging.getLogger(__name__)

class TextbookPipeline:
    def __init__(self):
        self.ncert_scraper = NCERTScraper()
        self.cisce_scraper = CISCEScraper()

    def run_for_book(self, book_code: str, board: str = "CBSE", class_name: str = "Unknown", subject: str = "Unknown"):
        """
        Runs the full pipeline for a single book.
        """
        logger.info(f"Starting pipeline for book: {book_code} ({board})")
        
        # 1. Generate URLs (Discovery)
        if board.upper() == "ICSE":
            urls = self.cisce_scraper.generate_chapter_urls(book_code)
        else:
            # Limit to 2 chapters for demo purposes
            urls = self.ncert_scraper.generate_chapter_urls(book_code, num_chapters=2)
        
        book_chapters = []
        total_pages_processed = 0
        
        # We need to process each chapter PDF separately and then combine?
        # OR does NCERT provide a single PDF?
        # Usually NCERT provides chapter-wise PDFs.
        # The requirements say "Download PDFs... Extracts chapter-level data".
        # If we have multiple PDFs per book, we should probably treat each PDF as a "Chapter" 
        # BUT the requirement says "Extracts chapter-level data: Chapter number, Chapter name, Start page, End page".
        # This implies we might be parsing a single large PDF or handling the chapter-wise PDFs and extracting internal structure.
        # If we download chapter-wise PDFs, the "Chapter Detection" is trivial (it's the file itself).
        # HOWEVER, the prompt mentions "Chapter Detection Engine... Font-Size... Regex... ToC".
        # This strongly suggests we are dealing with *combined* PDFs or we need to verify the content of chapter PDFs.
        # OR, we might be downloading a "Full Book" PDF if available.
        # NCERT sometimes has a "Download Complete Book" link.
        # Let's assume we might get a full book PDF or we treat each chapter PDF as a segment.
        # For the purpose of the "Chapter Detection Engine" requirement, it makes most sense if we are processing a file that *contains* multiple chapters.
        # If we only download single chapters, the "ToC Extraction" strategy is useless for that file (unless it has a ToC for the whole book).
        # I will assume we might be downloading a full book or we want to demonstrate the capability on whatever we get.
        # Let's try to download the "Complete Book" if possible.
        # NCERT zip files are available.
        # But for this pipeline, let's assume we process whatever PDF we get.
        # If we get chapter PDFs, we can still run the extractor to find sections *within* the chapter (like "Unit 1", "Section 1.1").
        # But the prompt says "Chapter number, Chapter name".
        # I will implement the loop to download *all* chapters, and then for each PDF, we run the extractor.
        # BUT, to show off the "Chapter Detection", I should probably try to merge them into one PDF or just process one large PDF.
        # Let's stick to processing each downloaded PDF.
        
        # Wait, if I download `lemh101.pdf`, it is "Chapter 1".
        # If I run "Chapter Detection" on it, I might find "Chapter 1: Real Numbers".
        # That satisfies the requirement.
        
        for url in urls:
            filename = url.split("/")[-1]
            save_path = PDF_DIR / board / class_name / subject / filename
            
            # 2. Download
            pdf_path = download_pdf(url, save_path)
            if not pdf_path:
                continue
                
            # 3. Parse
            # We use the filename (minus ext) as book_id for this segment
            segment_id = Path(filename).stem
            parser = PDFParser(pdf_path, segment_id)
            parse_result = parser.parse()
            
            if not parse_result:
                continue
                
            pages = parse_result.get("pages", [])
            layout = parse_result.get("layout", [])
            
            # 4. Extract Metadata
            meta_extractor = MetadataExtractor(pdf_path, pages)
            metadata = meta_extractor.extract()
            # Override with provided known info
            metadata["board"] = board
            metadata["class"] = class_name
            metadata["subject"] = subject
            
            # 5. Detect Chapters
            # Strategy A & B
            heading_extractor = HeadingExtractor(pages, layout)
            headings_A = heading_extractor.detect_by_fontsize()
            headings_B = heading_extractor.detect_by_regex()
            
            # Strategy C
            toc_extractor = ToCExtractor(pages)
            toc_chapters = toc_extractor.extract()
            
            # Merge
            merger = ChapterMerger(toc_chapters, headings_A + headings_B, len(pages))
            final_chapters = merger.merge()
            
            # 6. Export
            exporter = DataExporter(segment_id)
            exporter.export_json(metadata, final_chapters)
            exporter.export_csv(metadata, final_chapters)
            exporter.append_to_master_csv(metadata, final_chapters)
            exporter.append_to_master_json(metadata, final_chapters)
            exporter.update_metadata_index(metadata)
            
            logger.info(f"Completed processing for {filename}")

    def run_demo(self):
        """
        Runs a demo on a few known books.
        """
        books = self.ncert_scraper.discover_books()
        # Limit to 1 book for demo speed
        if books:
            book = books[0]
            self.run_for_book(
                book_code=book["book_code"],
                board=book["board"],
                class_name=book["class"],
                subject=book["subject"]
            )

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    pipeline = TextbookPipeline()
    pipeline.run_demo()
