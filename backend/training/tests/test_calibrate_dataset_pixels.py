"""
Tests for calibrate_dataset_pixels management command.
"""
import pytest
import json
import tempfile
import numpy as np
from pathlib import Path
from io import StringIO
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
from django.core.management import call_command
from django.core.management.base import CommandError

from training.management.commands.calibrate_dataset_pixels import Command


@pytest.mark.django_db
class TestCalibrateDatasetPixelsCommand:
    """Tests for calibrate_dataset_pixels command."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def mock_image(self, temp_dir):
        """Create mock image file."""
        image_path = temp_dir / "test_image.jpg"
        image = Image.new('RGB', (224, 224), color='red')
        image.save(image_path)
        return image_path
    
    @pytest.fixture
    def mock_calibration_file(self, temp_dir):
        """Create mock calibration file."""
        cal_file = temp_dir / "pixel_calibration.json"
        cal_data = {
            "calibration_records": [],
            "total_images": 0,
            "processed_count": 0,
            "skipped_count": 0,
            "error_count": 0
        }
        cal_file.write_text(json.dumps(cal_data), encoding='utf-8')
        return cal_file
    
    @pytest.fixture
    def mock_csv_data(self, temp_dir):
        """Create mock CSV data."""
        csv_path = temp_dir / "dataset.csv"
        csv_content = "id,alto,ancho,grosor,peso\n1,10.0,20.0,5.0,100.0\n"
        csv_path.write_text(csv_content, encoding='utf-8')
        return csv_path
    
    @patch('training.management.commands.calibrate_dataset_pixels.CacaoDatasetLoader')
    @patch('training.management.commands.calibrate_dataset_pixels.get_crops_dir')
    @patch('training.management.commands.calibrate_dataset_pixels.ensure_dir_exists')
    def test_load_existing_records(self, mock_ensure_dir, mock_crops_dir, mock_loader, temp_dir, mock_calibration_file):
        """Test loading existing calibration records."""
        command = Command()
        command.stdout = StringIO()
        
        records = command._load_existing_records(mock_calibration_file)
        
        assert isinstance(records, dict)
        assert len(records) == 0
    
    @patch('training.management.commands.calibrate_dataset_pixels.CacaoDatasetLoader')
    @patch('training.management.commands.calibrate_dataset_pixels.get_crops_dir')
    @patch('training.management.commands.calibrate_dataset_pixels.ensure_dir_exists')
    def test_load_existing_records_file_not_exists(self, mock_ensure_dir, mock_crops_dir, mock_loader, temp_dir):
        """Test loading when calibration file doesn't exist."""
        command = Command()
        command.stdout = StringIO()
        
        cal_file = temp_dir / "nonexistent.json"
        records = command._load_existing_records(cal_file)
        
        assert isinstance(records, dict)
        assert len(records) == 0
    
    @patch('training.management.commands.calibrate_dataset_pixels.CacaoDatasetLoader')
    @patch('training.management.commands.calibrate_dataset_pixels.get_crops_dir')
    @patch('training.management.commands.calibrate_dataset_pixels.ensure_dir_exists')
    def test_load_dataset(self, mock_ensure_dir, mock_crops_dir, mock_loader, temp_dir, mock_csv_data):
        """Test loading dataset."""
        import pandas as pd
        mock_loader_instance = Mock()
        mock_df = pd.DataFrame({'id': [1, 2], 'alto': [10, 20]})
        mock_valid_df = pd.DataFrame({'id': [1], 'alto': [10]})
        mock_loader_instance.load_dataset.return_value = mock_df
        mock_loader_instance.validate_images_exist.return_value = (mock_valid_df, [])
        mock_loader.return_value = mock_loader_instance
        mock_crops_dir.return_value = temp_dir
        
        command = Command()
        command.stdout = StringIO()
        
        loader, valid_df = command._load_dataset()
        
        assert loader is not None
        assert valid_df is not None
        assert len(valid_df) == 1
    
    @patch('builtins.__import__')
    def test_setup_segmentation_method_ai(self, mock_import):
        """Test setting up AI segmentation method."""
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = True
        mock_torch.cuda.get_device_name.return_value = "GPU"
        mock_props = MagicMock()
        mock_props.total_memory = 8 * 1024**3
        mock_torch.cuda.get_device_properties.return_value = mock_props
        
        def import_side_effect(name, *args, **kwargs):
            if name == 'torch':
                return mock_torch
            return __import__(name, *args, **kwargs)
        
        mock_import.side_effect = import_side_effect
        
        command = Command()
        command.stdout = StringIO()
        
        method = command._setup_segmentation_method('ai')
        
        assert method == 'ai'
    
    @patch('builtins.__import__')
    def test_setup_segmentation_method_cpu(self, mock_import):
        """Test setting up segmentation method with CPU."""
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = False
        
        def import_side_effect(name, *args, **kwargs):
            if name == 'torch':
                return mock_torch
            return __import__(name, *args, **kwargs)
        
        mock_import.side_effect = import_side_effect
        
        command = Command()
        command.stdout = StringIO()
        
        method = command._setup_segmentation_method('ai')
        
        assert method == 'ai'
    
    def test_measure_pixels_rgba(self):
        """Test measuring pixels from RGBA image."""
        command = Command()
        
        # Create RGBA image array
        crop_array = np.zeros((100, 100, 4), dtype=np.uint8)
        crop_array[:, :, 3] = 255  # Full alpha
        
        crop_image = Image.fromarray(crop_array, 'RGBA')
        original_pixels = 100 * 100
        
        measurements = command._measure_pixels(crop_image, original_pixels)
        
        assert 'grain_area_pixels' in measurements
        assert 'width_pixels' in measurements
        assert 'height_pixels' in measurements
        assert 'background_ratio' in measurements
    
    def test_measure_pixels_rgb(self):
        """Test measuring pixels from RGB image."""
        command = Command()
        
        # Create RGB image
        crop_image = Image.new('RGB', (100, 100), color='red')
        original_pixels = 100 * 100
        
        measurements = command._measure_pixels(crop_image, original_pixels)
        
        assert 'grain_area_pixels' in measurements
        assert measurements['grain_area_pixels'] > 0
    
    def test_calculate_scale_factors(self):
        """Test calculating scale factors."""
        command = Command()
        
        pixel_measurements = {
            'height_pixels': 120.0,
            'width_pixels': 100.0
        }
        real_dimensions = {
            'alto': 24.0,
            'ancho': 20.0
        }
        
        scale_factors = command._calculate_scale_factors(pixel_measurements, real_dimensions)
        
        assert 'alto_mm_per_pixel' in scale_factors
        assert 'ancho_mm_per_pixel' in scale_factors
        assert 'average_mm_per_pixel' in scale_factors
        assert scale_factors['alto_mm_per_pixel'] == 24.0 / 120.0
        assert scale_factors['ancho_mm_per_pixel'] == 20.0 / 100.0
    
    def test_calculate_scale_factors_zero_pixels(self):
        """Test calculating scale factors with zero pixels."""
        command = Command()
        
        pixel_measurements = {
            'height_pixels': 0.0,
            'width_pixels': 0.0
        }
        real_dimensions = {
            'alto': 24.0,
            'ancho': 20.0
        }
        
        scale_factors = command._calculate_scale_factors(pixel_measurements, real_dimensions)
        
        assert scale_factors['alto_mm_per_pixel'] == 0.0
        assert scale_factors['ancho_mm_per_pixel'] == 0.0
        assert scale_factors['average_mm_per_pixel'] == 0.0
    
    def test_create_calibration_record(self):
        """Test creating calibration record."""
        command = Command()
        
        image_id = 1
        image_path = Path("test.jpg")
        processed_png_path = Path("processed.png")
        pixel_measurements = {
            'grain_area_pixels': 8000,
            'width_pixels': 100,
            'height_pixels': 120,
            'background_pixels': 2000,
            'background_ratio': 0.2
        }
        real_dimensions = {
            'alto': 24.0,
            'ancho': 20.0,
            'grosor': 5.0,
            'peso': 100.0
        }
        scale_factors = {
            'alto_mm_per_pixel': 0.2,
            'ancho_mm_per_pixel': 0.2,
            'average_mm_per_pixel': 0.2
        }
        original_pixels_total = 12000
        confidence = 0.95
        
        record = command._create_calibration_record(
            image_id, image_path, processed_png_path, pixel_measurements,
            real_dimensions, scale_factors, original_pixels_total, confidence
        )
        
        assert record['id'] == image_id
        assert 'real_dimensions' in record
        assert 'pixel_measurements' in record
        assert 'scale_factors' in record
        assert record['segmentation_confidence'] == 0.95
    
    def test_calculate_basic_stats(self):
        """Test calculating basic statistics."""
        command = Command()
        
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        stats = command._calculate_basic_stats(values)
        
        assert 'mean' in stats
        assert 'std' in stats
        assert 'min' in stats
        assert 'max' in stats
        assert stats['mean'] == 3.0
        assert stats['min'] == 1.0
        assert stats['max'] == 5.0
    
    def test_calculate_basic_stats_empty(self):
        """Test calculating statistics with empty list."""
        command = Command()
        
        stats = command._calculate_basic_stats([])
        
        assert stats['mean'] == 0
        assert stats['std'] == 0
        assert stats['min'] == 0
        assert stats['max'] == 0
    
    def test_calculate_basic_stats_use_int(self):
        """Test calculating statistics with integer min/max."""
        command = Command()
        
        values = [1.5, 2.5, 3.5]
        stats = command._calculate_basic_stats(values, use_int_min_max=True)
        
        assert isinstance(stats['min'], int)
        assert isinstance(stats['max'], int)
    
    def test_calculate_scale_factor_stats(self):
        """Test calculating scale factor statistics."""
        command = Command()
        
        calibration_data = [
            {'scale_factors': {'average_mm_per_pixel': 0.2}},
            {'scale_factors': {'average_mm_per_pixel': 0.3}},
            {'scale_factors': {'average_mm_per_pixel': 0.25}}
        ]
        
        stats = command._calculate_scale_factor_stats(calibration_data)
        
        assert 'mean' in stats
        assert 'std' in stats
        assert 'median' in stats
        assert stats['mean'] > 0
    
    def test_calculate_scale_factor_stats_empty(self):
        """Test calculating scale factor statistics with empty data."""
        command = Command()
        
        stats = command._calculate_scale_factor_stats([])
        
        assert stats['mean'] == 0
        assert stats['median'] == 0
    
    def test_calculate_pixel_dimension_stats(self):
        """Test calculating pixel dimension statistics."""
        command = Command()
        
        calibration_data = [
            {
                'pixel_measurements': {
                    'height_pixels': 120,
                    'width_pixels': 100,
                    'grain_area_pixels': 8000
                }
            },
            {
                'pixel_measurements': {
                    'height_pixels': 130,
                    'width_pixels': 110,
                    'grain_area_pixels': 9000
                }
            }
        ]
        
        stats = command._calculate_pixel_dimension_stats(calibration_data)
        
        assert 'height' in stats
        assert 'width' in stats
        assert 'area' in stats
    
    def test_calculate_real_dimension_stats(self):
        """Test calculating real dimension statistics."""
        command = Command()
        
        calibration_data = [
            {
                'real_dimensions': {
                    'alto_mm': 24.0,
                    'ancho_mm': 20.0,
                    'peso_g': 100.0
                }
            },
            {
                'real_dimensions': {
                    'alto_mm': 26.0,
                    'ancho_mm': 22.0,
                    'peso_g': 110.0
                }
            }
        ]
        
        stats = command._calculate_real_dimension_stats(calibration_data)
        
        assert 'alto' in stats
        assert 'ancho' in stats
        assert 'peso' in stats
    
    def test_calculate_calibration_statistics(self):
        """Test calculating complete calibration statistics."""
        command = Command()
        
        calibration_data = [
            {
                'scale_factors': {'average_mm_per_pixel': 0.2},
                'pixel_measurements': {
                    'height_pixels': 120,
                    'width_pixels': 100,
                    'grain_area_pixels': 8000
                },
                'real_dimensions': {
                    'alto_mm': 24.0,
                    'ancho_mm': 20.0,
                    'peso_g': 100.0
                }
            }
        ]
        
        stats = command._calculate_calibration_statistics(calibration_data)
        
        assert 'scale_factors' in stats
        assert 'pixel_dimensions' in stats
        assert 'real_dimensions' in stats
    
    def test_calculate_calibration_statistics_empty(self):
        """Test calculating statistics with empty data."""
        command = Command()
        
        stats = command._calculate_calibration_statistics([])
        
        assert stats == {}
    
    @patch('training.management.commands.calibrate_dataset_pixels.CacaoDatasetLoader')
    @patch('training.management.commands.calibrate_dataset_pixels.get_crops_dir')
    @patch('training.management.commands.calibrate_dataset_pixels.ensure_dir_exists')
    @patch('ml.segmentation.processor.segment_and_crop_cacao_bean')
    @patch('training.management.commands.calibrate_dataset_pixels.get_crop_image_path')
    def test_segment_image_primary(self, mock_get_crop_path, mock_segment, mock_ensure_dir, mock_crops_dir, mock_loader, temp_dir, mock_image):
        """Test primary segmentation method."""
        mock_segment.return_value = str(temp_dir / "crop.png")
        mock_get_crop_path.return_value = temp_dir / "processed.png"
        mock_ensure_dir.return_value = None
        
        # Create crop image
        crop_image = Image.new('RGBA', (100, 100), color=(255, 0, 0, 255))
        crop_image.save(temp_dir / "crop.png")
        
        command = Command()
        command.stdout = StringIO()
        
        crop_image, processed_path, confidence = command._segment_image_primary(
            mock_image, 'ai', 1
        )
        
        assert crop_image is not None
        assert confidence == 0.95
    
    @patch('training.management.commands.calibrate_dataset_pixels.get_crop_image_path')
    @patch('ml.segmentation.cropper.create_cacao_cropper')
    def test_segment_image_fallback(self, mock_create_cropper, mock_get_crop_path, temp_dir, mock_image):
        """Test fallback segmentation method."""
        mock_cropper = Mock()
        mock_cropper.process_image.return_value = {
            'success': True,
            'crop_path': str(temp_dir / "crop.png"),
            'confidence': 0.85
        }
        mock_create_cropper.return_value = mock_cropper
        mock_get_crop_path.return_value = temp_dir / "processed.png"
        
        # Create crop image
        crop_image = Image.new('RGBA', (100, 100), color=(255, 0, 0, 255))
        crop_image.save(temp_dir / "crop.png")
        
        command = Command()
        command.stdout = StringIO()
        
        crop_image, processed_path, confidence = command._segment_image_fallback(
            mock_image, 1
        )
        
        assert crop_image is not None
        assert confidence == 0.85
    
    @patch('ml.segmentation.processor.segment_and_crop_cacao_bean')
    @patch('ml.segmentation.cropper.create_cacao_cropper')
    @patch('training.management.commands.calibrate_dataset_pixels.get_crop_image_path')
    def test_segment_image_fallback_on_error(self, mock_get_crop_path, mock_create_cropper, mock_segment, temp_dir, mock_image):
        """Test segmentation falls back on primary error."""
        mock_segment.side_effect = Exception("Primary failed")
        mock_cropper = Mock()
        mock_cropper.process_image.return_value = {
            'success': True,
            'crop_path': str(temp_dir / "crop.png"),
            'confidence': 0.85
        }
        mock_create_cropper.return_value = mock_cropper
        mock_get_crop_path.return_value = temp_dir / "processed.png"
        
        # Create crop image
        crop_image = Image.new('RGBA', (100, 100), color=(255, 0, 0, 255))
        crop_image.save(temp_dir / "crop.png")
        
        command = Command()
        command.stdout = StringIO()
        
        crop_image, processed_path, confidence = command._segment_image(
            mock_image, 'ai', 1
        )
        
        assert crop_image is not None

