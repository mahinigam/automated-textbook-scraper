import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class ChapterMerger:
    def __init__(self, toc_chapters: List[Dict], heading_chapters: List[Dict], total_pages: int):
        self.toc_chapters = toc_chapters
        self.heading_chapters = heading_chapters
        self.total_pages = total_pages

    def merge(self) -> List[Dict]:
        """
        Merges chapters from different strategies.
        """
        final_chapters = []
        
        # 1. Prefer ToC if available and looks reasonable
        if self.toc_chapters and len(self.toc_chapters) > 0:
            logger.info(f"Using ToC chapters as primary source ({len(self.toc_chapters)} found).")
            final_chapters = self.toc_chapters
        else:
            logger.info("Using Heading Detection (Font/Regex) as primary source.")
            # Deduplicate heading chapters based on page number
            # If multiple on same page, pick highest score
            page_map = {}
            for ch in self.heading_chapters:
                p = ch['page_num']
                if p not in page_map or ch['score'] > page_map[p]['score']:
                    page_map[p] = ch
            
            final_chapters = sorted(page_map.values(), key=lambda x: x['page_num'])

        # 2. Post-process: Add end_page and format
        processed = []
        for i, ch in enumerate(final_chapters):
            start = ch.get('start_page') or ch.get('page_num')
            
            # Determine end page
            if i < len(final_chapters) - 1:
                next_start = final_chapters[i+1].get('start_page') or final_chapters[i+1].get('page_num')
                end = next_start - 1
            else:
                end = self.total_pages
                
            if end < start:
                end = start # Should not happen but safety check
                
            processed.append({
                "chapter_no": i + 1,
                "chapter_name": ch.get('chapter_name') or ch.get('text') or f"Chapter {i+1}",
                "start_page": start,
                "end_page": end,
                "source_strategy": ch.get('type', 'unknown')
            })
            
        return processed
