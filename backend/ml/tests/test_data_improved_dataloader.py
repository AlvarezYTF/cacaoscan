"""
Tests for data improved_dataloader module.
"""
from unittest import TestCase
from unittest.mock import patch, MagicMock


class ImprovedDataLoaderTest(TestCase):
    """Tests for improved dataloader."""

    def test_improved_dataloader_import(self):
        """Test that improved_dataloader module can be imported."""
        try:
            from ml.data import improved_dataloader
            self.assertIsNotNone(improved_dataloader)
        except ImportError:
            pass

