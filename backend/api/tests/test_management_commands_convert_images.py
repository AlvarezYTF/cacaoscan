"""
Tests for convert_cacao_images management command.
"""
import pytest
from io import StringIO
from pathlib import Path
from unittest.mock import patch, MagicMock
from django.core.management import call_command
from django.core.management.base import CommandError


@pytest.mark.django_db
class TestConvertCacaoImagesCommand:
    """Tests for convert_cacao_images command."""
    
    @patch('api.management.commands.convert_cacao_images.get_raw_images_dir')
    @patch('api.management.commands.convert_cacao_images.get_converted_jpg_dir')
    @patch('api.management.commands.convert_cacao_images.get_processed_images_dir')
    @patch('api.management.commands.convert_cacao_images.ensure_dir_exists')
    @patch('api.management.commands.convert_cacao_images.convert_bmp_to_jpg')
    @patch('api.management.commands.convert_cacao_images.segment_and_crop_cacao_bean')
    @patch('api.management.commands.convert_cacao_images.save_image')
    def test_handle_only_bmp(self, mock_save, mock_segment, mock_convert_bmp, 
                             mock_ensure_dir, mock_png_dir, mock_jpg_dir, mock_raw_dir, temp_dir):
        """Test command with --only bmp option."""
        # Setup mocks
        mock_raw_dir.return_value = temp_dir / "raw"
        mock_jpg_dir.return_value = temp_dir / "jpg"
        mock_png_dir.return_value = temp_dir / "png"
        mock_ensure_dir.side_effect = lambda p: p
        
        # Create mock BMP file
        bmp_file = temp_dir / "raw" / "test.bmp"
        bmp_file.parent.mkdir(parents=True, exist_ok=True)
        bmp_file.touch()
        
        # Mock conversion result
        mock_image = MagicMock()
        mock_convert_bmp.return_value = (mock_image, {"success": True})
        
        out = StringIO()
        call_command('convert_cacao_images', '--only', 'bmp', '--limit', '1', stdout=out)
        
        output = out.getvalue()
        assert mock_convert_bmp.called
        assert mock_save.called
    
    @patch('api.management.commands.convert_cacao_images.get_raw_images_dir')
    @patch('api.management.commands.convert_cacao_images.get_converted_jpg_dir')
    @patch('api.management.commands.convert_cacao_images.get_processed_images_dir')
    @patch('api.management.commands.convert_cacao_images.ensure_dir_exists')
    @patch('api.management.commands.convert_cacao_images.convert_bmp_to_jpg')
    @patch('api.management.commands.convert_cacao_images.segment_and_crop_cacao_bean')
    @patch('api.management.commands.convert_cacao_images.save_image')
    def test_handle_only_png(self, mock_save, mock_segment, mock_convert_bmp,
                             mock_ensure_dir, mock_png_dir, mock_jpg_dir, mock_raw_dir, temp_dir):
        """Test command with --only png option."""
        # Setup mocks
        mock_raw_dir.return_value = temp_dir / "raw"
        mock_jpg_dir.return_value = temp_dir / "jpg"
        mock_png_dir.return_value = temp_dir / "png"
        mock_ensure_dir.side_effect = lambda p: p
        
        # Create mock JPG file
        jpg_file = temp_dir / "jpg" / "test.jpg"
        jpg_file.parent.mkdir(parents=True, exist_ok=True)
        jpg_file.touch()
        
        # Mock segmentation result
        mock_image = MagicMock()
        mock_segment.return_value = (mock_image, {"success": True})
        
        out = StringIO()
        call_command('convert_cacao_images', '--only', 'png', '--limit', '1', stdout=out)
        
        output = out.getvalue()
        assert mock_segment.called
        assert mock_save.called
    
    @patch('api.management.commands.convert_cacao_images.get_raw_images_dir')
    @patch('api.management.commands.convert_cacao_images.get_converted_jpg_dir')
    @patch('api.management.commands.convert_cacao_images.get_processed_images_dir')
    @patch('api.management.commands.convert_cacao_images.ensure_dir_exists')
    def test_handle_no_images(self, mock_ensure_dir, mock_png_dir, mock_jpg_dir, mock_raw_dir, temp_dir):
        """Test command with no images to process."""
        # Setup mocks
        mock_raw_dir.return_value = temp_dir / "raw"
        mock_jpg_dir.return_value = temp_dir / "jpg"
        mock_png_dir.return_value = temp_dir / "png"
        mock_ensure_dir.side_effect = lambda p: p
        
        # Create empty directories
        (temp_dir / "raw").mkdir(parents=True, exist_ok=True)
        (temp_dir / "jpg").mkdir(parents=True, exist_ok=True)
        (temp_dir / "png").mkdir(parents=True, exist_ok=True)
        
        out = StringIO()
        call_command('convert_cacao_images', '--only', 'bmp', stdout=out)
        
        output = out.getvalue()
        assert 'completado' in output.lower() or 'procesado' in output.lower()
    
    @patch('api.management.commands.convert_cacao_images.get_raw_images_dir')
    @patch('api.management.commands.convert_cacao_images.get_converted_jpg_dir')
    @patch('api.management.commands.convert_cacao_images.get_processed_images_dir')
    @patch('api.management.commands.convert_cacao_images.ensure_dir_exists')
    @patch('api.management.commands.convert_cacao_images.convert_bmp_to_jpg')
    @patch('api.management.commands.convert_cacao_images.save_image')
    def test_handle_conversion_failure(self, mock_save, mock_convert_bmp,
                                      mock_ensure_dir, mock_png_dir, mock_jpg_dir, mock_raw_dir, temp_dir):
        """Test command handles conversion failures gracefully."""
        # Setup mocks
        mock_raw_dir.return_value = temp_dir / "raw"
        mock_jpg_dir.return_value = temp_dir / "jpg"
        mock_png_dir.return_value = temp_dir / "png"
        mock_ensure_dir.side_effect = lambda p: p
        
        # Create mock BMP file
        bmp_file = temp_dir / "raw" / "test.bmp"
        bmp_file.parent.mkdir(parents=True, exist_ok=True)
        bmp_file.touch()
        
        # Mock conversion failure
        mock_convert_bmp.return_value = (None, {"success": False, "error": "Conversion failed"})
        
        out = StringIO()
        call_command('convert_cacao_images', '--only', 'bmp', '--limit', '1', stdout=out)
        
        output = out.getvalue()
        assert not mock_save.called


@pytest.mark.django_db
class TestConvertCacaoImagesTrainingCommand:
    """Tests for training/management/commands/convert_cacao_images (wrapper)."""
    
    def test_command_is_wrapper(self):
        """Test that training command is a wrapper around api command."""
        from training.management.commands.convert_cacao_images import Command
        from api.management.commands.convert_cacao_images import Command as ApiCommand
        
        assert Command is ApiCommand

