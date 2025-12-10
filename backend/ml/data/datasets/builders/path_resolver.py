"""
Path resolver for dataset records.

This module handles resolving and validating file paths,
following Single Responsibility Principle.
"""
from pathlib import Path
from typing import Dict

from ....utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.data.datasets.builders.path_resolver")


class PathResolver:
    """
    Resolver for dataset file paths.
    
    This class is responsible for:
    - Resolving relative and absolute paths
    - Validating path existence
    - Normalizing path formats
    
    Following Single Responsibility Principle.
    """
    
    def __init__(self, base_dir: Path):
        """
        Initialize path resolver.
        
        Args:
            base_dir: Base directory for resolving relative paths
        """
        self.base_dir = base_dir
        logger.debug(f"PathResolver initialized (base_dir={base_dir})")
    
    def resolve(self, record: Dict) -> Path:
        """
        Resolve crop path from record.
        
        Args:
            record: Dataset record dictionary
            
        Returns:
            Resolved Path object
        """
        crop_path = Path(record.get("crop_image_path", ""))
        
        if crop_path.is_absolute():
            return crop_path
        
        resolved_path = self.base_dir / crop_path
        logger.debug(f"Resolved path: {crop_path} -> {resolved_path}")
        return resolved_path
    
    def exists(self, path: Path) -> bool:
        """
        Check if path exists.
        
        Args:
            path: Path to check
            
        Returns:
            True if path exists, False otherwise
        """
        return path.exists()

