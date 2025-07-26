"""
Document type specific handlers
"""

import re
from typing import Dict, List, Any, Optional
from utils import PATTERNS, is_contact_info

class DocumentTypeDetector:
    """Detect and handle different document types."""
    
    def __init__(self):
        self.promotional_indicators = [
            "you're invited", "hope to see you", "party", "celebration",
            "join us", "rsvp", "required", "please visit", "event",
            "special", "don't miss", "save the date", "come join"
        ]
        
        self.formal_indicators = [
            "introduction", "conclusion", "methodology", "abstract",
            "chapter", "section", "appendix", "references", "table of contents",
            "executive summary", "background", "literature review"
        ]
        
        self.academic_indicators = [
            "abstract", "thesis", "dissertation", "research", "hypothesis",
            "methodology", "results", "discussion", "conclusion", "bibliography"
        ]
    
    def detect_document_type(self, text_sample: str) -> str:
        """Detect document type from content analysis."""
        text_lower = text_sample.lower()
        
        # Count different indicators
        promotional_count = sum(1 for indicator in self.promotional_indicators
                              if indicator in text_lower)
        formal_count = sum(1 for indicator in self.formal_indicators
                          if indicator in text_lower)
        academic_count = sum(1 for indicator in self.academic_indicators
                           if indicator in text_lower)
        
        # Check for contact information (indicates promotional)
        contact_patterns = [PATTERNS['phone'], PATTERNS['url'], PATTERNS['address']]
        contact_count = sum(1 for pattern in contact_patterns
                          if pattern.search(text_lower))
        
        # Decision logic
        if promotional_count >= 2 or contact_count >= 2:
            return "promotional"
        elif academic_count >= 2:
            return "academic"
        elif formal_count >= 2:
            return "formal"
        else:
            return "general"

class PromotionalHandler:
    """Handler for promotional documents like invitations."""
    
    def __init__(self):
        self.high_priority_phrases = [
            "you're invited", "hope to see you", "party", "celebration",
            "join us", "rsvp", "required", "please visit", "come join",
            "special event", "don't miss", "save the date"
        ]
    
    def is_promotional_heading(self, text: str, font_size: float, is_bold: bool,
                             is_centered: bool, avg_font_size: float) -> bool:
        """Determine if text is a promotional heading."""
        text_lower = text.lower().strip()
        
        # Skip empty or very short text
        if len(text) < 3:
            return False
        
        # Skip contact information unless strongly emphasized
        if is_contact_info(text):
            return is_bold and font_size > avg_font_size + 2
        
        # High-priority promotional phrases
        for phrase in self.high_priority_phrases:
            if phrase in text_lower:
                return True
        
        # Visual emphasis criteria
        emphasis_score = 0
        
        # Font size emphasis
        if font_size > avg_font_size + 2:
            emphasis_score += 3
        elif font_size > avg_font_size + 1:
            emphasis_score += 2
        
        # Bold emphasis
        if is_bold:
            emphasis_score += 2
        
        # Centered text (common in invitations)
        if is_centered:
            emphasis_score += 2
        
        # Case emphasis
        if text.isupper() and len(text) > 4:
            emphasis_score += 2
        elif text.istitle():
            emphasis_score += 1
        
        # Exclamation marks
        if '!' in text:
            emphasis_score += 1
        
        # Need sufficient emphasis
        return emphasis_score >= 3
    
    def calculate_importance_score(self, text: str, font_size: float,
                                 is_bold: bool, is_centered: bool,
                                 avg_font_size: float, page_position: float) -> float:
        """Calculate importance score for promotional content ranking."""
        score = 0.0
        text_lower = text.lower()
        
        # High-priority phrase bonuses
        for phrase in self.high_priority_phrases:
            if phrase in text_lower:
                score += 10
        
        # Font size relative importance
        size_ratio = font_size / max(avg_font_size, 1)
        score += size_ratio * 3
        
        # Visual emphasis
        if is_bold:
            score += 4
        if is_centered:
            score += 3
        if text.isupper():
            score += 2
        
        # Exclamation emphasis
        score += text.count('!') * 1.5
        
        # Position bonuses (top and bottom are important in invitations)
        if page_position < 0.3:  # Top of page
            score += 2
        elif page_position > 0.7:  # Bottom of page
            score += 1
        
        # Length considerations
        if 5 <= len(text) <= 50:  # Optimal heading length
            score += 1
        elif len(text) > 100:  # Too long for heading
            score -= 2
        
        return score

class FormalHandler:
    """Handler for formal documents."""
    
    def __init__(self):
        self.section_patterns = [
            re.compile(r'^\d+\.?\s+', re.IGNORECASE),  # Numbered sections
            re.compile(r'^[ivxlcdm]+\.?\s+', re.IGNORECASE),  # Roman numerals
            re.compile(r'^(chapter|section|part)\s+\d+', re.IGNORECASE)
        ]
    
    def is_formal_heading(self, text: str, font_size: float, is_bold: bool,
                        is_centered: bool, is_top: bool, avg_font_size: float) -> bool:
        """Determine if text is a formal heading."""
        # Size-based detection
        if font_size >= avg_font_size + 2:
            return True
        
        # Bold + case pattern
        if is_bold and (text.isupper() or text.istitle()):
            return True
        
        # Layout-based detection
        if (is_centered or is_top) and (text.isupper() or text.istitle()):
            return True
        
        # Pattern-based detection
        for pattern in self.section_patterns:
            if pattern.match(text):
                return True
        
        return False
    
    def detect_heading_level(self, text: str, font_size: float, is_bold: bool,
                           is_centered: bool, is_top: bool, avg_font_size: float) -> Optional[str]:
        """Detect heading level for formal documents."""
        if not self.is_formal_heading(text, font_size, is_bold, is_centered, is_top, avg_font_size):
            return None
        
        # H1 - Largest headings
        if font_size >= avg_font_size + 4:
            return "H1"
        
        # H1 - Centered, large, bold
        if is_centered and is_bold and font_size >= avg_font_size + 2:
            return "H1"
        
        # H2 - Large headings
        if font_size >= avg_font_size + 2:
            return "H2"
        
        # H2 - Bold with good size
        if is_bold and font_size >= avg_font_size + 1:
            return "H2"
        
        # H3 - Everything else
        return "H3"
