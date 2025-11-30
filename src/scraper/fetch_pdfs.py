import os
import time
import logging
import requests
import hashlib
from pathlib import Path
from typing import Optional
from .config import HEADERS, REQUEST_DELAY, MAX_RETRIES, TIMEOUT

logger = logging.getLogger(__name__)

def calculate_checksum(file_path: Path) -> str:
    """Calculates SHA256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def download_pdf(url: str, save_path: Path, overwrite: bool = False) -> Optional[Path]:
    """
    Downloads a PDF from a URL to the specified path.
    
    Args:
        url: The URL to download from.
        save_path: The local path to save the file.
        overwrite: Whether to overwrite existing files.
        
    Returns:
        Path to the saved file if successful, None otherwise.
    """
    if save_path.exists() and not overwrite:
        logger.info(f"File already exists: {save_path}")
        return save_path

    save_path.parent.mkdir(parents=True, exist_ok=True)
    
    temp_path = save_path.with_suffix(".tmp")
    
    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"Downloading {url} (Attempt {attempt + 1}/{MAX_RETRIES})")
            response = requests.get(url, headers=HEADERS, stream=True, timeout=TIMEOUT)
            response.raise_for_status()
            
            with open(temp_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # Rename temp file to actual file
            temp_path.rename(save_path)
            logger.info(f"Successfully downloaded: {save_path}")
            
            # Polite delay
            time.sleep(REQUEST_DELAY)
            return save_path
            
        except requests.RequestException as e:
            logger.error(f"Error downloading {url}: {e}")
            if temp_path.exists():
                temp_path.unlink()
            time.sleep(REQUEST_DELAY * (attempt + 1))
            
    logger.error(f"Failed to download {url} after {MAX_RETRIES} attempts")
    return None
