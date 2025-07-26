"""
Utility functions for PDF text analysis
Performance optimized with caching
"""

import re
import numpy as np
from typing import List, Dict, Any, Optional
from functools import lru_cache

# Cached regex patterns for performance
PATTERNS = {
    'noise': re.compile(r'^\d+$|^page\s+\d+|^fig\w*\s*\d+|^table\s*\d+|^www\.|^https?://|^\[.*\]$|^copyright|^all rights reserved|^©|^\s*$', re.IGNORECASE),
    'numbered': re.compile(r'^(\d+\.?\d*\s*)', re.IGNORECASE),
    'roman': re.compile(r'^[ivxlcdm]+\.?\s+', re.IGNORECASE),
    'phone': re.compile(r'\(\d{3}\)\s*\d{3}-\d{4}|\d{3}-\d{3}-\d{4}|\d{10}'),
    'url': re.compile(r'www\.|https?://|\.com\b|\.org\b|\.net\b', re.IGNORECASE),
    'address': re.compile(r'\d+\s+[\w\s]+(?:street|st|avenue|ave|road|rd|drive|dr|lane|ln|way|blvd|boulevard)', re.IGNORECASE),
    'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
    'bullet': re.compile(r'^[•·▪▫◦‣⁃]\s+', re.IGNORECASE)
}

def is_bold(span: Dict[str, Any]) -> bool:
    """Bold detection - removed caching due to dict parameter."""
    if not isinstance(span, dict):
        return False
    
    font_name = span.get("font", "").lower()
    flags = span.get("flags", 0)
    
    # Font name indicators
    bold_indicators = ["bold", "black", "heavy", "semibold", "demi"]
    font_bold = any(indicator in font_name for indicator in bold_indicators)
    
    # Flags check (bit 4 for bold in PyMuPDF)
    flag_bold = (flags & 16) != 0
    
    return font_bold or flag_bold

def is_italic(span: Dict[str, Any]) -> bool:
    """Check if text is italic - removed caching due to dict parameter."""
    if not isinstance(span, dict):
        return False
    
    font_name = span.get("font", "").lower()
    flags = span.get("flags", 0)
    
    italic_indicators = ["italic", "oblique"]
    font_italic = any(indicator in font_name for indicator in italic_indicators)
    flag_italic = (flags & 2) != 0
    
    return font_italic or flag_italic

def is_centered(block: Dict[str, Any], page_width: float, tolerance: float = 0.15) -> bool:
    """Center detection."""
    bbox = block.get("bbox", [0, 0, 0, 0])
    if not bbox or len(bbox) < 4:
        return False
    
    block_center = (bbox[0] + bbox[2]) / 2
    page_center = page_width / 2
    return abs(block_center - page_center) / page_width < tolerance

def is_top_of_page(block: Dict[str, Any], page_height: float, max_pct: float = 0.25) -> bool:
    """Check if block is at top of page."""
    bbox = block.get("bbox", [0, 0, 0, 0])
    if not bbox or len(bbox) < 4:
        return False
    return bbox[1] < page_height * max_pct

def is_bottom_of_page(block: Dict[str, Any], page_height: float, min_pct: float = 0.75) -> bool:
    """Check if block is at bottom of page."""
    bbox = block.get("bbox", [0, 0, 0, 0])
    if not bbox or len(bbox) < 4:
        return False
    return bbox[1] > page_height * min_pct

@lru_cache(maxsize=2000)
def is_heading_case(text: str) -> bool:
    """Heading case detection with caching - text is hashable."""
    if not text:
        return False
    
    # All uppercase
    if text.isupper() and len(text) > 2:
        return True
    
    # Title case
    if text.istitle():
        return True
    
    # Numbered headings
    if PATTERNS['numbered'].match(text):
        return True
    
    # Roman numerals
    if PATTERNS['roman'].match(text):
        return True
    
    return False

@lru_cache(maxsize=2000)
def clean_heading_text(text: str) -> str:
    """Clean and normalize heading text."""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove trailing punctuation
    text = re.sub(r'[.\-_]+$', '', text)
    
    # Remove page numbers at the end
    text = re.sub(r'\s+\d+$', '', text)
    
    return text.strip()

@lru_cache(maxsize=2000)
def is_noise_text(text: str) -> bool:
    """Detect noise text that shouldn't be considered as headings."""
    if not text:
        return True
    
    text_clean = text.strip()
    
    # Use cached pattern
    if PATTERNS['noise'].match(text_clean):
        return True
    
    # Very short text (but allow some short meaningful headings)
    if len(text_clean) < 2:
        return True
    
    # Pure numbers
    if text_clean.isdigit():
        return True
    
    # URLs and emails
    if PATTERNS['url'].search(text_clean) or PATTERNS['email'].search(text_clean):
        return True
    
    return False

def calculate_text_stats(blocks: List[Dict[str, Any]]) -> Dict[str, float]:
    """Calculate text statistics for the document."""
    font_sizes = []
    line_heights = []
    
    for block in blocks:
        if "lines" not in block:
            continue
        
        for line in block["lines"]:
            for span in line["spans"]:
                if span.get("text", "").strip():
                    font_sizes.append(span.get("size", 12))
                    
            bbox = line.get("bbox", [0, 0, 0, 0])
            if len(bbox) >= 4:
                line_heights.append(bbox[3] - bbox[1])
    
    if not font_sizes:
        return {
            "avg_font_size": 12,
            "max_font_size": 12,
            "min_font_size": 12,
            "std_font_size": 0,
            "avg_line_height": 15,
            "total_text_blocks": 0
        }
    
    font_sizes_np = np.array(font_sizes)
    line_heights_np = np.array(line_heights) if line_heights else np.array([15])
    
    return {
        "avg_font_size": float(np.mean(font_sizes_np)),
        "max_font_size": float(np.max(font_sizes_np)),
        "min_font_size": float(np.min(font_sizes_np)),
        "std_font_size": float(np.std(font_sizes_np)),
        "avg_line_height": float(np.mean(line_heights_np)),
        "total_text_blocks": len(font_sizes)
    }

# Rest of the functions remain the same...
def detect_outline_from_toc(doc) -> List[Dict[str, Any]]:
    """Extract outline from document's table of contents."""
    outline = []
    
    try:
        toc = doc.get_toc()
        if not toc:
            return outline
        
        for item in toc:
            if len(item) >= 3:
                level, title, page = item[0], item[1], item[2]
                
                # Convert level to H1, H2, H3 format
                if 1 <= level <= 3:
                    heading_level = f"H{level}"
                    cleaned_title = clean_heading_text(title)
                    
                    if cleaned_title and len(cleaned_title) > 1:
                        outline.append({
                            "level": heading_level,
                            "text": cleaned_title,
                            "page": max(1, int(page))
                        })
    except Exception:
        pass
    
    return outline

@lru_cache(maxsize=2000)
def is_contact_info(text: str) -> bool:
    """Check if text contains contact information."""
    text_lower = text.lower()
    
    # Phone numbers
    if PATTERNS['phone'].search(text):
        return True
    
    # URLs
    if PATTERNS['url'].search(text_lower):
        return True
    
    # Email patterns
    if PATTERNS['email'].search(text):
        return True
    
    # Address patterns
    if PATTERNS['address'].search(text):
        return True
    
    return False

def extract_page_position(block: Dict[str, Any], page_height: float) -> float:
    """Extract relative position of block on page (0.0 = top, 1.0 = bottom)"""
    bbox = block.get("bbox", [0, 0, 0, 0])
    if not bbox or len(bbox) < 4:
        return 0.0
    return bbox[1] / max(page_height, 1)

def validate_heading_hierarchy(outline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Validate and fix heading hierarchy."""
    if not outline:
        return outline
    
    # Sort by page and original order
    outline_sorted = sorted(outline, key=lambda x: (x['page'], x.get('order', 0)))
    
    # Validate hierarchy
    validated = []
    last_level = 0
    
    for heading in outline_sorted:
        current_level = int(heading['level'][1])  # Extract number from H1, H2, H3
        
        # Ensure proper hierarchy - don't skip levels
        if current_level > last_level + 1:
            current_level = last_level + 1
            heading['level'] = f"H{current_level}"
        
        validated.append(heading)
        last_level = current_level
    
    return validated

def merge_similar_headings(headings: List[Dict[str, Any]], similarity_threshold: float = 0.8) -> List[Dict[str, Any]]:
    """Merge similar headings to reduce duplicates"""
    if not headings:
        return headings
    
    merged = []
    seen_text = set()
    
    for heading in headings:
        text = heading['text'].lower().strip()
        
        # Simple duplicate check
        if text in seen_text:
            continue
        
        seen_text.add(text)
        merged.append(heading)
    
    return merged
