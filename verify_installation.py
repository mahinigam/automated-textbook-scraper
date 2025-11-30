import sys
import logging
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.parser.pdf_parser import PDFParser
from src.extractor.headings import HeadingExtractor
from src.extractor.toc import ToCExtractor
from src.extractor.merger import ChapterMerger
from src.extractor.metadata import MetadataExtractor
from src.exporter import DataExporter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def create_dummy_pdf(path: Path):
    """Creates a dummy PDF with known structure."""
    c = canvas.Canvas(str(path), pagesize=letter)
    width, height = letter
    
    # Page 1: Title
    c.setFont("Helvetica-Bold", 24)
    c.drawString(100, 700, "Mathematics Class 10")
    c.setFont("Helvetica", 12)
    c.drawString(100, 650, "Board: CBSE")
    c.showPage()
    
    # Page 2: ToC
    c.setFont("Helvetica-Bold", 18)
    c.drawString(100, 700, "Table of Contents")
    c.setFont("Helvetica", 12)
    c.drawString(100, 650, "Chapter 1: Real Numbers ....... 3")
    c.drawString(100, 630, "Chapter 2: Polynomials ........ 5")
    c.showPage()
    
    # Page 3: Chapter 1 Start
    c.setFont("Helvetica-Bold", 20)
    c.drawString(100, 700, "Chapter 1")
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 670, "Real Numbers")
    c.setFont("Helvetica", 12)
    c.drawString(100, 600, "Introduction to Real Numbers...")
    c.showPage()
    
    # Page 4: Chapter 1 Content
    c.drawString(100, 700, "More content...")
    c.showPage()
    
    # Page 5: Chapter 2 Start
    c.setFont("Helvetica-Bold", 20)
    c.drawString(100, 700, "Chapter 2")
    c.drawString(100, 670, "Polynomials")
    c.showPage()
    
    c.save()
    logger.info(f"Created dummy PDF at {path}")

def verify_system():
    logger.info("Starting System Verification...")
    
    # Setup paths
    base_dir = Path("verification_data")
    base_dir.mkdir(exist_ok=True)
    pdf_path = base_dir / "test_book.pdf"
    
    # 1. Create Dummy PDF
    try:
        import reportlab
    except ImportError:
        logger.error("reportlab is required for this verification script. Please install it: pip install reportlab")
        return

    create_dummy_pdf(pdf_path)
    
    # 2. Parse
    logger.info("Running Parser...")
    parser = PDFParser(pdf_path, "test_book")
    parse_result = parser.parse()
    pages = parse_result["pages"]
    layout = parse_result["layout"]
    
    if not pages:
        logger.error("Parsing failed!")
        return

    # 3. Extract Metadata
    logger.info("Running Metadata Extractor...")
    meta_extractor = MetadataExtractor(pdf_path, pages)
    metadata = meta_extractor.extract()
    logger.info(f"Extracted Metadata: {metadata}")
    
    # 4. Detect Chapters
    logger.info("Running Chapter Detection...")
    heading_extractor = HeadingExtractor(pages, layout)
    headings_A = heading_extractor.detect_by_fontsize()
    headings_B = heading_extractor.detect_by_regex()
    
    toc_extractor = ToCExtractor(pages)
    toc_chapters = toc_extractor.extract()
    
    merger = ChapterMerger(toc_chapters, headings_A + headings_B, len(pages))
    final_chapters = merger.merge()
    
    logger.info(f"Detected {len(final_chapters)} chapters.")
    for ch in final_chapters:
        logger.info(f" - {ch['chapter_name']} (Page {ch['start_page']}-{ch['end_page']})")
        
    # 5. Export
    logger.info("Running Exporter...")
    exporter = DataExporter("test_book", output_dir=base_dir / "outputs")
    exporter.export_json(metadata, final_chapters)
    exporter.export_csv(metadata, final_chapters)
    
    # Verification Checks
    success = True
    if metadata["subject"] != "Mathematics":
        logger.error("Metadata Subject mismatch!")
        success = False
    if len(final_chapters) != 2:
        logger.error("Chapter count mismatch!")
        success = False
        
    if success:
        logger.info("\n✅ SYSTEM VERIFICATION PASSED! The pipeline is working correctly.")
    else:
        logger.error("\n❌ SYSTEM VERIFICATION FAILED.")

if __name__ == "__main__":
    verify_system()
