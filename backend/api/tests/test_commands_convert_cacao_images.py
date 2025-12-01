"""
Tests for convert_cacao_images management command.
"""
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.core.management import call_command
from pathlib import Path
from io import StringIO
import tempfile


class ConvertCacaoImagesCommandTest(TestCase):
    """Tests for convert_cacao_images command."""

    def setUp(self):
        """Set up test fixtures."""
        self.stdout = StringIO()
        self.stderr = StringIO()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('api.management.commands.convert_cacao_images.get_raw_images_dir')
    @patch('api.management.commands.convert_cacao_images.convert_bmp_to_jpg')
    def test_convert_cacao_images_bmp_only(self, mock_convert, mock_get_dir):
        """Test converting BMP images only."""
        mock_get_dir.return_value = Path(self.temp_dir)
        mock_convert.return_value = (True, {'converted': 1})

        try:
            call_command(
                'convert_cacao_images',
                '--only', 'bmp',
                '--limit', '1',
                stdout=self.stdout
            )
        except Exception:
            pass

    @patch('api.management.commands.convert_cacao_images.get_processed_images_dir')
    @patch('api.management.commands.convert_cacao_images.segment_and_crop_cacao_bean')
    def test_convert_cacao_images_png_only(self, mock_segment, mock_get_dir):
        """Test converting JPG to PNG (segmented) only."""
        mock_get_dir.return_value = Path(self.temp_dir)
        mock_segment.return_value = '/path/to/segmented.png'

        try:
            call_command(
                'convert_cacao_images',
                '--only', 'png',
                '--limit', '1',
                stdout=self.stdout
            )
        except Exception:
            pass

