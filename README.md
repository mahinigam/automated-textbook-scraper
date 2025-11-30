# Automated CBSE/ICSE Textbook Scraper + Metadata Extractor

## Overview
This project provides an end-to-end automated pipeline to discover, download, and parse CBSE/ICSE textbooks. It extracts structured metadata and chapter-level details, handling both searchable and scanned PDFs with OCR fallback.

## Architecture
For a detailed explanation of the design and thought process, please see [APPROACH.md](APPROACH.md).

1. **Scraper**: Crawls official sources (NCERT/CBSE) to discover and download PDFs.
2. **Parser**: Uses `pdfplumber` for text/layout extraction and `Tesseract` for OCR on scanned pages.
3. **Chapter Detection**: Uses font-size analysis, regex patterns, and Table of Contents extraction to identify chapters.
4. **Metadata Extractor**: Extracts board, class, and subject information.
5. **Output**: Generates JSON and CSV files with structured data.

## Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd instavise_textbook_pipeline
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Install Tesseract OCR**:
    - **macOS**: `brew install tesseract`
    - **Ubuntu**: `sudo apt-get install tesseract-ocr`
    - **Windows**: Download installer from UB Mannheim.

## Usage

### Running the Pipeline
You can run the full pipeline using the demo notebook:
`notebooks/demo_pipeline.ipynb`

### Running Tests
```bash
pytest tests/
```

## Project Structure
```
instavise_textbook_pipeline/
├── notebooks/          # Jupyter notebooks
├── src/
│   ├── scraper/        # Web scraping logic
│   ├── parser/         # PDF parsing and OCR
│   └── extractor/      # Metadata and chapter extraction
├── data/               # Data storage (pdfs, parsed, outputs)
└── tests/              # Unit tests
```
