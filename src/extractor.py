"""
Main heading extraction logic - Heuristic Only
Enhanced for better accuracy and performance
"""

import fitz  # PyMuPDF
import time
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from detector import HeuristicDetector
from document_types import PromotionalHandler
from utils import (
    is_bold, is_italic, is_centered, is_top_of_page, is_bottom_of_page,
    clean_heading_text, is_heading_case, is_noise_text, is_contact_info,
    calculate_text_stats, detect_outline_from_toc, extract_page_position,
    validate_heading_hierarchy, merge_similar_headings
)

# Set up logging
logger = logging.getLogger(__name__)

def extract_outline(pdf_path: str) -> Dict[str, Any]:
    """
    Main function to extract document outline using heuristic approach only.
    Enhanced with better document type detection and improved accuracy.
    """
    start_time = time.time()
    doc = None
    
    try:
        doc = fitz.open(pdf_path)
        logger.info(f"Successfully opened PDF: {pdf_path}")
    except Exception as e:
        logger.error(f"Failed to open PDF: {e}")
        return {
            "title": "Error: Could not open PDF",
            "outline": [],
            "metadata": {"error": str(e)}
        }
    
    try:
        # Initialize detector
        detector = HeuristicDetector()
        
        # First, try extracting from built-in TOC
        toc_outline = detect_outline_from_toc(doc)
        
        # If TOC is substantial, use it as primary source
        if len(toc_outline) >= 3:
            title = extract_title(doc)
            total_pages = len(doc)
            doc.close()
            doc = None  # Mark as closed
            return {
                "title": title,
                "outline": toc_outline,
                "metadata": {
                    "extraction_method": "toc",
                    "processing_time": time.time() - start_time,
                    "total_pages": total_pages
                }
            }
        
        # Detect document type from content
        doc_type = detect_document_type(doc)
        logger.info(f"Detected document type: {doc_type}")
        
        # Calculate document statistics from first few pages
        all_blocks = []
        pages_to_sample = min(len(doc), 5)
        for page_num in range(pages_to_sample):
            try:
                page = doc[page_num]
                blocks = page.get_text("dict")["blocks"]
                all_blocks.extend(blocks)
            except Exception as e:
                logger.warning(f"Error reading page {page_num}: {e}")
                continue
        
        stats = calculate_text_stats(all_blocks)
        
        # Extract title
        title = extract_title(doc, stats)
        
        # Extract headings based on document type
        outline = []
        seen_headings = set()
        total_pages = len(doc)
        
        for page_num in range(total_pages):
            try:
                page = doc[page_num]
                blocks = page.get_text("dict")["blocks"]
                page_width, page_height = page.rect.width, page.rect.height
                
                page_headings = extract_page_headings(
                    blocks, page_num + 1, page_width, page_height,
                    stats, detector, doc_type, seen_headings
                )
                
                outline.extend(page_headings)
                seen_headings.update(h["text"] for h in page_headings)
                
            except Exception as e:
                logger.warning(f"Error processing page {page_num + 1}: {e}")
                continue
        
        # Post-process outline
        outline = post_process_outline(outline, doc_type, detector)
        
        # Close document before returning
        doc.close()
        doc = None  # Mark as closed
        
        return {
            "title": title,
            "outline": outline,
            "metadata": {
                "extraction_method": "heuristic",
                "document_type": doc_type,
                "processing_time": time.time() - start_time,
                "total_pages": total_pages,
                "total_headings": len(outline)
            }
        }
    
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        
        # Ensure document is closed even on error
        if doc is not None:
            try:
                doc.close()
            except:
                pass
        
        return {
            "title": "Error: Processing failed",
            "outline": [],
            "metadata": {
                "error": str(e),
                "processing_time": time.time() - start_time
            }
        }

def detect_document_type(doc) -> str:
    """Detect document type from content analysis."""
    try:
        # Sample first few pages for performance
        sample_pages = min(3, len(doc))
        total_text = ""
        
        for page_num in range(sample_pages):
            try:
                page = doc[page_num]
                text = page.get_text().lower()
                total_text += text
            except Exception as e:
                logger.warning(f"Error reading page {page_num} for type detection: {e}")
                continue
        
        # Use heuristic detector for document type detection
        detector = HeuristicDetector()
        return detector.detect_document_type(total_text)
    
    except Exception as e:
        logger.warning(f"Error detecting document type: {e}")
        return "general"

def extract_title(doc, stats: Dict[str, float] = None) -> str:
    """Extract document title using multiple strategies."""
    try:
        # Strategy 1: PDF metadata
        metadata = doc.metadata
        if metadata and metadata.get("title"):
            title = metadata["title"].strip()
            if title and not title.lower().endswith('.pdf'):
                return clean_heading_text(title)
    except Exception as e:
        logger.warning(f"Error reading PDF metadata: {e}")
    
    # Strategy 2: First page analysis
    try:
        if len(doc) > 0:
            page = doc[0]
            blocks = page.get_text("dict")["blocks"]
            page_width, page_height = page.rect.width, page.rect.height
            
            if not stats:
                stats = calculate_text_stats(blocks)
            
            title_candidates = []
            
            for block in blocks:
                if "lines" not in block:
                    continue
                
                for line in block["lines"]:
                    spans = line["spans"]
                    if not spans:
                        continue
                    
                    text = "".join(span["text"] for span in spans).strip()
                    text = clean_heading_text(text)
                    
                    if not text or len(text) < 5 or is_noise_text(text):
                        continue
                    
                    # Calculate title score
                    score = calculate_title_score(text, spans, block, page_width, 
                                                page_height, stats)
                    title_candidates.append((score, text))
            
            # Return highest scoring title
            if title_candidates:
                title_candidates.sort(reverse=True)
                return title_candidates[0][1]
    
    except Exception as e:
        logger.warning(f"Error extracting title from first page: {e}")
    
    return ""

def calculate_title_score(text: str, spans: List[Dict[str, Any]],
                         block: Dict[str, Any], page_width: float,
                         page_height: float, stats: Dict[str, float]) -> float:
    """Calculate title likelihood score."""
    try:
        score = 0.0
        
        # Font size score
        avg_size = sum(span.get("size", 12) for span in spans) / len(spans)
        size_ratio = avg_size / max(stats["avg_font_size"], 1)
        score += min(size_ratio * 2, 5)
        
        # Bold bonus
        bold_spans = sum(is_bold(span) for span in spans)
        if bold_spans / len(spans) > 0.5:
            score += 3
        
        # Centered bonus
        if is_centered(block, page_width, tolerance=0.2):
            score += 3
        
        # Top of page bonus
        if is_top_of_page(block, page_height, max_pct=0.3):
            score += 2
        
        # Length considerations
        if 10 <= len(text) <= 80:  # Optimal title length
            score += 2
        elif len(text) > 100:
            score -= 2
        
        # Case bonus
        if is_heading_case(text):
            score += 1
        
        # Penalize contact info and noise
        if is_contact_info(text) or is_noise_text(text):
            score -= 5
        
        return score
    
    except Exception as e:
        logger.warning(f"Error calculating title score: {e}")
        return 0.0

def extract_page_headings(blocks: List[Dict[str, Any]], page_num: int,
                         page_width: float, page_height: float,
                         stats: Dict[str, float], detector: HeuristicDetector,
                         doc_type: str, seen_headings: set) -> List[Dict[str, Any]]:
    """Extract headings from a single page."""
    try:
        headings = []
        
        # Handle promotional content separately
        if doc_type == "promotional":
            return extract_promotional_headings(
                blocks, page_num, page_width, page_height, stats, seen_headings
            )
        
        # Standard heading extraction
        for order, block in enumerate(blocks):
            if "lines" not in block:
                continue
            
            for line in block["lines"]:
                spans = line["spans"]
                if not spans:
                    continue
                
                text = "".join(span["text"] for span in spans).strip()
                text = clean_heading_text(text)
                
                if not text or len(text) < 2 or text in seen_headings:
                    continue
                
                # Calculate text properties
                font_sizes = [span.get("size", 12) for span in spans]
                avg_size = sum(font_sizes) / len(font_sizes)
                
                bold_spans = [is_bold(span) for span in spans]
                is_bold_text = sum(bold_spans) / len(bold_spans) > 0.5
                
                # Layout analysis
                centered = is_centered(block, page_width)
                top = is_top_of_page(block, page_height)
                
                # Detect heading level
                level = detector.detect_heading_level(
                    text, avg_size, is_bold_text, stats["avg_font_size"],
                    centered, top, doc_type
                )
                
                if level:
                    headings.append({
                        "level": level,
                        "text": text,
                        "page": page_num,
                        # "order": order,
                        # "confidence": "heuristic"
                    })
        
        return headings
    
    except Exception as e:
        logger.warning(f"Error extracting headings from page {page_num}: {e}")
        return []

def extract_promotional_headings(blocks: List[Dict[str, Any]], page_num: int,
                               page_width: float, page_height: float,
                               stats: Dict[str, float], seen_headings: set) -> List[Dict[str, Any]]:
    """Extract headings from promotional content like party invitations."""
    try:
        promotional_handler = PromotionalHandler()
        text_candidates = []
        
        for block in blocks:
            if "lines" not in block:
                continue
            
            for line in block["lines"]:
                spans = line["spans"]
                if not spans:
                    continue
                
                text = "".join(span["text"] for span in spans).strip()
                text = clean_heading_text(text)
                
                if not text or len(text) < 2 or text in seen_headings:
                    continue
                
                # Calculate text properties
                font_sizes = [span.get("size", 12) for span in spans]
                avg_size = sum(font_sizes) / len(font_sizes)
                
                bold_spans = [is_bold(span) for span in spans]
                is_bold_text = sum(bold_spans) / len(bold_spans) > 0.5
                
                # Layout analysis
                centered = is_centered(block, page_width)
                page_position = extract_page_position(block, page_height)
                
                # Check if it's a promotional heading
                if promotional_handler.is_promotional_heading(
                    text, avg_size, is_bold_text, centered, stats["avg_font_size"]
                ):
                    importance = promotional_handler.calculate_importance_score(
                        text, avg_size, is_bold_text, centered,
                        stats["avg_font_size"], page_position
                    )
                    
                    text_candidates.append({
                        "text": text,
                        "importance": importance,
                        "page": page_num
                    })
        
        # Sort by importance and assign levels
        text_candidates.sort(key=lambda x: x["importance"], reverse=True)
        headings = []
        
        for i, candidate in enumerate(text_candidates[:5]):  # Limit to top 5
            if i == 0:
                level = "H1"
            elif i <= 2:
                level = "H2"
            else:
                level = "H3"
            
            headings.append({
                "level": level,
                "text": candidate["text"],
                "page": candidate["page"],
                # "confidence": "promotional"
            })
        
        return headings
    
    except Exception as e:
        logger.warning(f"Error extracting promotional headings from page {page_num}: {e}")
        return []

def post_process_outline(outline: List[Dict[str, Any]], doc_type: str,
                        detector: HeuristicDetector) -> List[Dict[str, Any]]:
    """Post-process and refine the extracted outline."""
    try:
        if not outline:
            return outline
        
        # Remove duplicates
        outline = merge_similar_headings(outline)
        
        # Validate hierarchy
        outline = validate_heading_hierarchy(outline)
        
        # Rank by importance
        outline = detector.rank_headings_by_importance(outline, doc_type)
        
        # Limit results based on document type
        if doc_type == "promotional":
            return outline[:5]  # Limit promotional content
        else:
            return outline[:50]  # Standard limit
    
    except Exception as e:
        logger.warning(f"Error post-processing outline: {e}")
        return outline[:10]  # Return first 10 as fallback
