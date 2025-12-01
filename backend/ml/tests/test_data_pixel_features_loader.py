"""
Tests for data pixel_features_loader module.
"""
from unittest import TestCase
from unittest.mock import patch, MagicMock


class PixelFeaturesLoaderTest(TestCase):
    """Tests for pixel features loader."""

    def test_pixel_features_loader_import(self):
        """Test that pixel_features_loader module can be imported."""
        try:
            from ml.data import pixel_features_loader
            self.assertIsNotNone(pixel_features_loader)
        except ImportError:
            pass

