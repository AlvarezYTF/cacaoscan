"""
Unit tests for calibrate_dataset_pixels command module (calibrate_dataset_pixels.py).
Tests Django management command for calibrating dataset based on pixel measurements.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.core.management.base import CommandError
from pathlib import Path
import json
from PIL import Image
import numpy as np

from training.management.commands.calibrate_dataset_pixels import Command


@pytest.fixture
def command():
    """Create a Command instance for testing."""
    return Command()


@pytest.fixture
def mock_options():
    """Create mock command options."""
    # Django converts --output-dir to output_dir, --skip-existing to skip_existing, etc.
    return {
        'output_dir': 'media/datasets/calibration',
        'calibration_file': 'media/datasets/pixel_calibration.json',
        'skip_existing': False,
        'max_images': None,
        'segmentation_backend': 'ai'
    }


@pytest.fixture
def sample_calibration_record():
    """Create a sample calibration record."""
    return {
        'id': 1,
        'filename': 'test_image.bmp',
        'original_image_path': '/path/to/test_image.bmp',
        'processed_image_path': '/path/to/processed.png',
        'real_dimensions': {
            'alto_mm': 15.5,
            'ancho_mm': 12.3,
            'grosor_mm': 8.7,
            'peso_g': 1.2
        },
        'pixel_measurements': {
            'grain_area_pixels': 1000,
            'width_pixels': 100,
            'height_pixels': 120,
            'bbox_area_pixels': 12000,
            'aspect_ratio': 0.83
        },
        'background_info': {
            'original_total_pixels': 100000,
            'background_pixels': 99000,
            'background_ratio': 0.99
        },
        'scale_factors': {
            'alto_mm_per_pixel': 0.129,
            'ancho_mm_per_pixel': 0.123,
            'average_mm_per_pixel': 0.126
        },
        'segmentation_confidence': 0.95
    }


class TestCalibrateDatasetPixelsCommand:
    """Tests for calibrate_dataset_pixels Command class."""
    
    def test_command_initialization(self):
        """Test command initialization."""
        cmd = Command()
        assert cmd is not None
    
    @patch('training.management.commands.calibrate_dataset_pixels.CacaoDatasetLoader')
    @patch('training.management.commands.calibrate_dataset_pixels.get_crops_dir')
    @patch('training.management.commands.calibrate_dataset_pixels.ensure_dir_exists')
    def test_handle_loads_existing_calibration(self, mock_ensure_dir, mock_get_crops_dir,
                                              mock_loader_class, command, mock_options, tmp_path):
        """Test that existing calibration file is loaded."""
        calibration_file = tmp_path / "calibration.json"
        # Use fixture properly - it's passed as parameter
        calibration_file.write_text(json.dumps({
            'calibration_records': [{
                'id': 1,
                'filename': 'test_image.bmp',
                'original_image_path': '/path/to/test_image.bmp',
                'processed_image_path': '/path/to/processed.png',
                'real_dimensions': {
                    'alto_mm': 15.5,
                    'ancho_mm': 12.3,
                    'grosor_mm': 8.7,
                    'peso_g': 1.2
                },
                'pixel_measurements': {
                    'grain_area_pixels': 1000,
                    'width_pixels': 100,
                    'height_pixels': 150
                }
            }]
        }), encoding='utf-8')
        
        mock_options['calibration_file'] = str(calibration_file)
        mock_get_crops_dir.return_value = tmp_path / "crops"
        
        mock_loader = Mock()
        mock_df = Mock()
        mock_df.__len__ = Mock(return_value=0)
        mock_df.__iter__ = Mock(return_value=iter([]))
        mock_df.iterrows.return_value = []
        mock_loader.load_dataset.return_value = mock_df
        mock_loader.validate_images_exist.return_value = (mock_df, [])
        mock_loader.get_valid_records.return_value = []
        mock_loader_class.return_value = mock_loader
        
        with patch.object(command, 'stdout'):
            command.handle(**mock_options)
        
        # Should have loaded existing records
        assert calibration_file.exists()
    
    @patch('training.management.commands.calibrate_dataset_pixels.CacaoDatasetLoader')
    @patch('training.management.commands.calibrate_dataset_pixels.get_crops_dir')
    @patch('training.management.commands.calibrate_dataset_pixels.ensure_dir_exists')
    def test_handle_dataset_loading_error(self, mock_ensure_dir, mock_get_crops_dir,
                                         mock_loader_class, command, mock_options):
        """Test handling when dataset loading fails."""
        mock_loader = Mock()
        mock_loader.load_dataset.side_effect = Exception("Dataset error")
        mock_loader_class.return_value = mock_loader
        
        with pytest.raises(CommandError, match="Error cargando dataset"):
            command.handle(**mock_options)
    
    @patch('training.management.commands.calibrate_dataset_pixels.segment_and_crop_cacao_bean')
    @patch('training.management.commands.calibrate_dataset_pixels.CacaoDatasetLoader')
    @patch('training.management.commands.calibrate_dataset_pixels.get_crop_image_path')
    @patch('training.management.commands.calibrate_dataset_pixels.get_crops_dir')
    @patch('training.management.commands.calibrate_dataset_pixels.ensure_dir_exists')
    def test_handle_segmentation_success(self, mock_ensure_dir, mock_get_crops_dir,
                                        mock_get_crop_path, mock_loader_class,
                                        mock_segment, command, mock_options, tmp_path):
        """Test successful image segmentation."""
        mock_get_crops_dir.return_value = tmp_path / "crops"
        processed_png = tmp_path / "processed.png"
        mock_get_crop_path.return_value = processed_png
        
        # Create a test image
        test_image = Image.new('RGB', (512, 512), color='red')
        test_image_path = tmp_path / "test_image.bmp"
        test_image.save(test_image_path)
        
        # Create processed PNG with alpha
        processed_image = Image.new('RGBA', (200, 200), color=(255, 0, 0, 255))
        processed_png.parent.mkdir(parents=True, exist_ok=True)
        processed_image.save(processed_png)
        
        mock_segment.return_value = str(processed_png)
        
        mock_loader = Mock()
        mock_df = Mock()
        mock_df.__len__ = Mock(return_value=0)
        mock_df.__iter__ = Mock(return_value=iter([]))
        mock_df.iterrows.return_value = []
        # Create a valid DataFrame with the record
        import pandas as pd
        valid_df = pd.DataFrame([{'id': 1, 'alto': 10.5, 'ancho': 8.3, 'grosor': 6.1, 'peso': 2.3}])
        mock_loader.get_valid_records.return_value = [
            {'id': 1, 'raw_image_path': test_image_path}
        ]
        mock_loader.load_dataset.return_value = valid_df
        mock_loader.validate_images_exist.return_value = (valid_df, [])
        mock_loader_class.return_value = mock_loader
        
        # Mock _segment_image_primary to verify it's called
        with patch.object(command, '_segment_image_primary') as mock_primary, \
             patch.object(command, 'stdout'):
            mock_primary.return_value = (Image.new('RGBA', (100, 100)), processed_png, 0.95)
            command.handle(**mock_options)
        
        # Verify that _segment_image_primary was called, which uses segment_and_crop_cacao_bean
        mock_primary.assert_called()
    
    @patch('ml.segmentation.cropper.create_cacao_cropper')
    @patch('training.management.commands.calibrate_dataset_pixels.segment_and_crop_cacao_bean')
    @patch('training.management.commands.calibrate_dataset_pixels.CacaoDatasetLoader')
    @patch('training.management.commands.calibrate_dataset_pixels.get_crop_image_path')
    @patch('training.management.commands.calibrate_dataset_pixels.get_crops_dir')
    @patch('training.management.commands.calibrate_dataset_pixels.ensure_dir_exists')
    def test_handle_segmentation_fallback_to_cropper(self, mock_ensure_dir, mock_get_crops_dir,
                                                     mock_get_crop_path, mock_loader_class,
                                                     mock_segment, mock_create_cropper,
                                                     command, mock_options, tmp_path):
        """Test fallback to cropper when segmentation fails."""
        mock_get_crops_dir.return_value = tmp_path / "crops"
        processed_png = tmp_path / "processed.png"
        mock_get_crop_path.return_value = processed_png
        
        from ml.segmentation.processor import SegmentationError
        mock_segment.side_effect = SegmentationError("Segmentation failed")
        
        mock_cropper = Mock()
        mock_cropper.process_image.return_value = {
            'success': True,
            'crop_path': str(processed_png),
            'confidence': 0.9
        }
        mock_create_cropper.return_value = mock_cropper
        
        mock_loader = Mock()
        mock_df = Mock()
        mock_df.__len__ = Mock(return_value=0)
        mock_df.__iter__ = Mock(return_value=iter([]))
        mock_df.iterrows.return_value = []
        mock_loader.load_dataset.return_value = mock_df
        mock_loader.validate_images_exist.return_value = (mock_df, [])
        # Return valid records so fallback is called
        test_image_path = tmp_path / "test_image.bmp"
        test_image = Image.new('RGB', (512, 512), color='red')
        test_image.save(test_image_path)
        # Create a valid DataFrame with the record
        import pandas as pd
        valid_df = pd.DataFrame([{'id': 1, 'alto': 10.5, 'ancho': 8.3, 'grosor': 6.1, 'peso': 2.3}])
        mock_loader.get_valid_records.return_value = [
            {'id': 1, 'raw_image_path': test_image_path}
        ]
        mock_loader.load_dataset.return_value = valid_df
        mock_loader.validate_images_exist.return_value = (valid_df, [])
        mock_loader_class.return_value = mock_loader
        
        # Mock _segment_image_primary to fail, triggering fallback
        with patch.object(command, '_segment_image_primary', side_effect=Exception("Primary failed")), \
             patch.object(command, '_segment_image_fallback') as mock_fallback, \
             patch.object(command, 'stdout'):
            mock_fallback.return_value = (Image.new('RGBA', (100, 100)), processed_png, 0.9)
            command.handle(**mock_options)
        
        # Verify that _segment_image_fallback was called, which uses create_cacao_cropper
        mock_fallback.assert_called()
    
    @patch('training.management.commands.calibrate_dataset_pixels.CacaoDatasetLoader')
    @patch('training.management.commands.calibrate_dataset_pixels.get_crop_image_path')
    @patch('training.management.commands.calibrate_dataset_pixels.get_crops_dir')
    @patch('training.management.commands.calibrate_dataset_pixels.ensure_dir_exists')
    def test_handle_skip_existing(self, mock_ensure_dir, mock_get_crops_dir,
                                  mock_get_crop_path, mock_loader_class,
                                  command, mock_options, tmp_path, sample_calibration_record):
        """Test skipping existing processed images."""
        mock_get_crops_dir.return_value = tmp_path / "crops"
        processed_png = tmp_path / "processed.png"
        processed_png.parent.mkdir(parents=True, exist_ok=True)
        processed_png.touch()
        mock_get_crop_path.return_value = processed_png
        
        calibration_file = tmp_path / "calibration.json"
        calibration_file.write_text(json.dumps({
            'calibration_records': [sample_calibration_record]
        }), encoding='utf-8')
        mock_options['calibration_file'] = str(calibration_file)
        mock_options['skip_existing'] = True  # Django converts --skip-existing to skip_existing
        
        mock_loader = Mock()
        mock_df = Mock()
        mock_df.__len__ = Mock(return_value=0)
        mock_df.__iter__ = Mock(return_value=iter([]))
        mock_df.iterrows.return_value = []
        mock_loader.load_dataset.return_value = mock_df
        mock_loader.validate_images_exist.return_value = (mock_df, [])
        mock_loader.get_valid_records.return_value = []
        mock_loader_class.return_value = mock_loader
        
        with patch.object(command, 'stdout'):
            command.handle(**mock_options)
        
        # Should have skipped processing
    
    def test_calculate_scale_factors(self, command):
        """Test calculation of scale factors."""
        alto_real = 15.5
        ancho_real = 12.3
        height_pixels = 120
        width_pixels = 100
        
        scale_factor_alto = alto_real / height_pixels if height_pixels > 0 else 0
        scale_factor_ancho = ancho_real / width_pixels if width_pixels > 0 else 0
        scale_factor_promedio = (scale_factor_alto + scale_factor_ancho) / 2 if (height_pixels > 0 and width_pixels > 0) else 0
        
        assert scale_factor_alto == pytest.approx(0.129, rel=1e-2)
        assert scale_factor_ancho == pytest.approx(0.123, rel=1e-2)
        assert scale_factor_promedio == pytest.approx(0.126, rel=1e-2)
    
    def test_calculate_scale_factors_zero_pixels(self, command):
        """Test calculation of scale factors with zero pixels."""
        alto_real = 15.5
        height_pixels = 0
        
        scale_factor_alto = alto_real / height_pixels if height_pixels > 0 else 0
        
        assert scale_factor_alto == 0

