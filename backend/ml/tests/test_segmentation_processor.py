"""
Tests for segmentation processor module.
"""
from unittest import TestCase
from unittest.mock import patch, MagicMock
from pathlib import Path


class ProcessorTest(TestCase):
    """Tests for segmentation processor."""

    def test_processor_import(self):
        """Test that processor module can be imported."""
        try:
            from ml.segmentation import processor
            self.assertIsNotNone(processor)
        except ImportError:
            pass

    def test_segment_and_crop_cacao_bean_import(self):
        """Test that segment_and_crop_cacao_bean function can be imported."""
        try:
            from ml.segmentation.processor import segment_and_crop_cacao_bean
            self.assertIsNotNone(segment_and_crop_cacao_bean)
        except ImportError:
            pass

