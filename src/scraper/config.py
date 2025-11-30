import os
from pathlib import Path

# Base Directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
PDF_DIR = DATA_DIR / "pdfs"
PARSED_DIR = DATA_DIR / "parsed"
OUTPUT_DIR = DATA_DIR / "outputs"
METADATA_DIR = DATA_DIR / "metadata"

# Ensure directories exist
for d in [DATA_DIR, PDF_DIR, PARSED_DIR, OUTPUT_DIR, METADATA_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Scraper Settings
NCERT_BASE_URL = "https://ncert.nic.in/"
NCERT_TEXTBOOK_URL = "https://ncert.nic.in/textbook.php"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

REQUEST_DELAY = 2.0  # Seconds
MAX_RETRIES = 3
TIMEOUT = 30

# Headers
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
