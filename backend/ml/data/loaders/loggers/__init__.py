"""
Loggers for data validation.

This module provides classes for logging validation results,
following SOLID principles for separation of concerns.
"""

from .missing_image_logger import MissingImageLogger

__all__ = ['MissingImageLogger']

