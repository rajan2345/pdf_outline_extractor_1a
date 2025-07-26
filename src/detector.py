

"""
Enhanced Heuristic-based Heading Detection
"""

import re
from typing import Dict, List, Any, Optional

# Change these relative imports to absolute imports
from utils import (
    is_bold, is_italic, is_centered, is_top_of_page,
    clean_heading_text, is_heading_case, is_noise_text, PATTERNS
)
from document_types import DocumentTypeDetector, PromotionalHandler, FormalHandler

# Rest of the file remains exactly the same...


class HeuristicDetector:
    """
    Advanced rule-based heading detection using typography and layout analysis.
    Optimized for various document types with improved accuracy.
    """
    
    def __init__(self):
        self.doc_detector = DocumentTypeDetector()
        self.promotional_handler = PromotionalHandler()
        self.formal_handler = FormalHandler()
        
        # Enhanced pattern matching
        self.special_patterns = {
            'chapter_heading': re.compile(r'^(chapter|ch\.?)\s+\d+', re.IGNORECASE),
            'section_heading': re.compile(r'^(section|sec\.?)\s+\d+', re.IGNORECASE),
            'part_heading': re.compile(r'^(part|pt\.?)\s+[ivxlcdm\d]+', re.IGNORECASE),
            'appendix': re.compile(r'^(appendix|app\.?)\s*[a-z\d]*', re.IGNORECASE),
            'figure_table': re.compile(r'^(figure|fig\.?|table|tbl\.?)\s+\d+', re.IGNORECASE)
        }
    
    def detect_document_type(self, text_sample: str) -> str:
        """Detect document type to apply appropriate detection strategy."""
        return self.doc_detector.detect_document_type(text_sample)
    
    def is_likely_heading(self, text: str, font_size: float, is_bold: bool,
                         avg_font_size: float, is_centered: bool = False,
                         is_top: bool = False, doc_type: str = "general") -> bool:
        """
        Determine if text is likely a heading using enhanced heuristic rules.
        """
        if not text or len(text.strip()) < 2:
            return False
        
        # Filter out noise
        if is_noise_text(text):
            return False
        
        # Skip figure/table captions unless they're emphasized
        if self.special_patterns['figure_table'].match(text) and not is_bold:
            return False
        
        # Apply document-type specific logic
        if doc_type == "promotional":
            return self.promotional_handler.is_promotional_heading(
                text, font_size, is_bold, is_centered, avg_font_size
            )
        elif doc_type == "formal":
            return self.formal_handler.is_formal_heading(
                text, font_size, is_bold, is_centered, is_top, avg_font_size
            )
        else:
            return self._is_general_heading(text, font_size, is_bold,
                                          is_centered, is_top, avg_font_size)
    
    def _is_general_heading(self, text: str, font_size: float, is_bold: bool,
                          is_centered: bool, is_top: bool, avg_font_size: float) -> bool:
        """General heading detection for mixed document types."""
        # Strong visual indicators
        if font_size >= avg_font_size + 3:
            return True
        
        # Bold + significant size increase
        if is_bold and font_size >= avg_font_size + 1.5:
            return True
        
        # Layout emphasis
        if (is_centered or is_top) and is_heading_case(text):
            return True
        
        # Special patterns
        for pattern in self.special_patterns.values():
            if pattern.match(text):
                return True
        
        # Numbered or bulleted lists (but not figure/table)
        if (PATTERNS['numbered'].match(text) or PATTERNS['roman'].match(text)) and len(text) > 5:
            return True
        
        return False
    
    def detect_heading_level(self, text: str, font_size: float, is_bold: bool,
                           avg_font_size: float, is_centered: bool = False,
                           is_top: bool = False, doc_type: str = "general") -> Optional[str]:
        """
        Determine heading level (H1, H2, H3) based on visual hierarchy.
        """
        if not self.is_likely_heading(text, font_size, is_bold, avg_font_size,
                                    is_centered, is_top, doc_type):
            return None
        
        # Document-type specific level detection
        if doc_type == "promotional":
            return self._detect_promotional_level(text, font_size, is_bold,
                                                is_centered, avg_font_size)
        elif doc_type == "formal":
            return self.formal_handler.detect_heading_level(
                text, font_size, is_bold, is_centered, is_top, avg_font_size
            )
        else:
            return self._detect_general_level(text, font_size, is_bold,
                                            is_centered, is_top, avg_font_size)
    
    def _detect_promotional_level(self, text: str, font_size: float,
                                is_bold: bool, is_centered: bool,
                                avg_font_size: float) -> str:
        """Detect heading level for promotional content."""
        text_lower = text.lower()
        
        # H1 criteria - most important promotional phrases
        h1_phrases = ["you're invited", "hope to see you", "party", "celebration"]
        if any(phrase in text_lower for phrase in h1_phrases):
            return "H1"
        
        # H1 - Large, bold, centered text
        if (font_size > avg_font_size + 3 and is_bold and is_centered):
            return "H1"
        
        # H1 - Very large text
        if font_size > avg_font_size + 4:
            return "H1"
        
        # H2 criteria - secondary emphasis
        if (font_size > avg_font_size + 2 and (is_bold or is_centered)):
            return "H2"
        
        # H2 - All caps with moderate emphasis
        if text.isupper() and len(text) > 4 and font_size > avg_font_size:
            return "H2"
        
        # H3 - everything else that qualified as heading
        return "H3"
    
    def _detect_general_level(self, text: str, font_size: float, is_bold: bool,
                            is_centered: bool, is_top: bool, avg_font_size: float) -> str:
        """Detect heading level for general documents."""
        # H1 - Largest headings or special patterns
        if (font_size >= avg_font_size + 4 or
            self.special_patterns['chapter_heading'].match(text) or
            self.special_patterns['part_heading'].match(text)):
            return "H1"
        
        # H1 - Centered, large, bold
        if is_centered and is_bold and font_size >= avg_font_size + 2:
            return "H1"
        
        # H2 - Large headings or section patterns
        if (font_size >= avg_font_size + 2 or
            self.special_patterns['section_heading'].match(text)):
            return "H2"
        
        # H2 - Bold with good size
        if is_bold and font_size >= avg_font_size + 1:
            return "H2"
        
        # H3 - Everything else
        return "H3"
    
    def rank_headings_by_importance(self, headings: List[Dict[str, Any]],
                                  doc_type: str = "general") -> List[Dict[str, Any]]:
        """Rank headings by importance for the given document type."""
        if doc_type == "promotional":
            return self._rank_promotional_headings(headings)
        else:
            return self._rank_standard_headings(headings)
    
    def _rank_promotional_headings(self, headings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank promotional headings by importance."""
        def importance_score(heading):
            text_lower = heading['text'].lower()
            score = 0
            
            # High-priority phrases
            for phrase in self.promotional_handler.high_priority_phrases:
                if phrase in text_lower:
                    score += 10
            
            # Level-based scoring
            level_scores = {"H1": 8, "H2": 5, "H3": 2}
            score += level_scores.get(heading['level'], 0)
            
            # Length penalty for very long text
            if len(heading['text']) > 100:
                score -= 5
            
            return score
        
        return sorted(headings, key=importance_score, reverse=True)
    
    def _rank_standard_headings(self, headings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank standard headings by hierarchy."""
        # Sort by page, then by level, then by position
        level_order = {"H1": 1, "H2": 2, "H3": 3}
        return sorted(headings, key=lambda x: (
            x['page'],
            level_order.get(x['level'], 4),
            x.get('order', 0)
        ))
