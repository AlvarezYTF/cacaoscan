"""
Extraction strategies for pixel features.

This module provides different extraction strategies,
following Strategy Pattern and SOLID principles.
"""

from .base_strategy import ExtractionStrategy
from .path_extraction_strategy import PathExtractionStrategy
from .extended_extraction_strategy import ExtendedExtractionStrategy
from .basic_extraction_strategy import BasicExtractionStrategy
from .fallback_extraction_strategy import FallbackExtractionStrategy

__all__ = [
    'ExtractionStrategy',
    'PathExtractionStrategy',
    'ExtendedExtractionStrategy',
    'BasicExtractionStrategy',
    'FallbackExtractionStrategy'
]

