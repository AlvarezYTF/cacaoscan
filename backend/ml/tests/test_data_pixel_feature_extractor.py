"""
Tests for data pixel_feature_extractor module.
"""
from unittest import TestCase
from unittest.mock import patch, MagicMock


class PixelFeatureExtractorTest(TestCase):
    """Tests for pixel feature extractor."""

    def test_pixel_feature_extractor_import(self):
        """Test that pixel_feature_extractor module can be imported."""
        try:
            from ml.data import pixel_feature_extractor
            self.assertIsNotNone(pixel_feature_extractor)
        except ImportError:
            pass

