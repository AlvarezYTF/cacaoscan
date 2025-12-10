"""
Target normalization utilities.

This module provides classes for normalizing target values,
following SOLID principles for separation of concerns.
"""

from .target_normalizer import TargetNormalizer
from .factories import ScalerFactory
from .transformers import ArrayTransformer, SingleValueTransformer

__all__ = [
    'TargetNormalizer',
    'ScalerFactory',
    'ArrayTransformer',
    'SingleValueTransformer'
]

