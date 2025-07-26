"""
Adobe India Hackathon 2025 - Round 1A
PDF Outline Extraction Package - Heuristic Only
"""

__version__ = "2.0.0"
__author__ = "Adobe India Hackathon Team"

from extractor import extract_outline
from detector import HeuristicDetector
from utils import (
    is_bold, is_italic, is_centered, is_top_of_page,
    clean_heading_text, calculate_text_stats
)

__all__ = [
    'extract_outline',
    'HeuristicDetector',
    'is_bold',
    'is_italic', 
    'is_centered',
    'is_top_of_page',
    'clean_heading_text',
    'calculate_text_stats'
]

