"""
Encoding handler for file reading.

This module handles multiple encoding detection and decoding,
following Single Responsibility Principle.
"""
from typing import List
from pathlib import Path

from ....utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.data.datasets.builders.encoding_handler")


class EncodingHandler:
    """
    Handler for file encoding detection and decoding.
    
    This class is responsible for:
    - Detecting file encodings
    - Decoding file content with multiple encoding attempts
    - Providing fallback decoding strategies
    
    Following Single Responsibility Principle.
    """
    
    DEFAULT_ENCODINGS: List[str] = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    
    def __init__(self, encodings: List[str] | None = None):
        """
        Initialize encoding handler.
        
        Args:
            encodings: List of encodings to try (default: utf-8, latin-1, cp1252, iso-8859-1)
        """
        self.encodings = encodings or self.DEFAULT_ENCODINGS
        logger.debug(f"EncodingHandler initialized with {len(self.encodings)} encodings")
    
    def decode_file(self, file_path: Path) -> str:
        """
        Decode file content trying multiple encodings.
        
        Args:
            file_path: Path to file to decode
            
        Returns:
            Decoded file content as string
            
        Raises:
            UnicodeDecodeError: If all encodings fail
        """
        with open(file_path, 'rb') as file:
            raw_content = file.read()
        
        for encoding in self.encodings:
            try:
                decoded_content = raw_content.decode(encoding)
                logger.debug(f"Successfully decoded {file_path.name} with {encoding}")
                return decoded_content
            except UnicodeDecodeError:
                continue
        
        logger.warning(
            f"All encodings failed for {file_path.name}, using utf-8 with errors='ignore'"
        )
        return raw_content.decode('utf-8', errors='ignore')

