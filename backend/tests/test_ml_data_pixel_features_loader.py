"""
Unit tests for pixel features loader (pixel_features_loader.py).
Tests PixelFeaturesLoader functionality.
"""
import pytest
import json
import numpy as np
from pathlib import Path
from unittest.mock import patch, mock_open

from ml.data.pixel_features_loader import PixelFeaturesLoader


@pytest.fixture
def sample_calibration_data():
    """Create sample calibration data for testing."""
    return {
        "calibration_records": [
            {
                "id": 1,
                "filename": "1.bmp",
                "pixel_measurements": {
                    "width_pixels": 100.0,
                    "height_pixels": 150.0,
                    "grain_area_pixels": 12000.0,
                    "bbox_area_pixels": 15000.0,
                    "aspect_ratio": 0.67
                },
                "scale_factors": {
                    "average_mm_per_pixel": 0.035
                },
                "background_info": {
                    "background_ratio": 0.2
                }
            },
            {
                "id": 2,
                "filename": "2.bmp",
                "pixel_measurements": {
                    "width_pixels": 110.0,
                    "height_pixels": 160.0,
                    "grain_area_pixels": 15000.0,
                    "bbox_area_pixels": 17600.0,
                    "aspect_ratio": 0.69
                },
                "scale_factors": {
                    "average_mm_per_pixel": 0.036
                },
                "background_info": {
                    "background_ratio": 0.15
                }
            }
        ]
    }


@pytest.fixture
def calibration_file(tmp_path, sample_calibration_data):
    """Create a calibration file for testing."""
    calib_file = tmp_path / "pixel_calibration.json"
    with open(calib_file, 'w', encoding='utf-8') as f:
        json.dump(sample_calibration_data, f, indent=2)
    return calib_file


class TestPixelFeaturesLoader:
    """Tests for PixelFeaturesLoader class."""
    
    def test_initialization_default_path(self):
        """Test initialization with default path."""
        with patch('ml.data.pixel_features_loader.get_datasets_dir', return_value=Path('/tmp')):
            loader = PixelFeaturesLoader()
            
            assert loader.calibration_file == Path('/tmp') / "pixel_calibration.json"
            assert loader._loaded is False
    
    def test_initialization_custom_path(self, calibration_file):
        """Test initialization with custom path."""
        loader = PixelFeaturesLoader(calibration_file=calibration_file)
        
        assert loader.calibration_file == calibration_file
    
    def test_load_success(self, calibration_file):
        """Test successful loading of calibration data."""
        loader = PixelFeaturesLoader(calibration_file=calibration_file)
        
        result = loader.load()
        
        assert result is True
        assert loader._loaded is True
        assert len(loader.features_by_id) == 2
        assert 1 in loader.features_by_id
        assert 2 in loader.features_by_id
    
    def test_load_file_not_found(self, tmp_path):
        """Test loading when file doesn't exist."""
        calib_file = tmp_path / "nonexistent.json"
        loader = PixelFeaturesLoader(calibration_file=calib_file)
        
        result = loader.load()
        
        assert result is False
        assert loader._loaded is False
    
    def test_load_empty_records(self, tmp_path):
        """Test loading with empty calibration records."""
        calib_file = tmp_path / "empty.json"
        empty_data = {"calibration_records": []}
        
        with open(calib_file, 'w', encoding='utf-8') as f:
            json.dump(empty_data, f)
        
        loader = PixelFeaturesLoader(calibration_file=calib_file)
        result = loader.load()
        
        assert result is False
        assert loader._loaded is False
    
    def test_load_invalid_json(self, tmp_path):
        """Test loading with invalid JSON."""
        calib_file = tmp_path / "invalid.json"
        calib_file.write_text("invalid json content")
        
        loader = PixelFeaturesLoader(calibration_file=calib_file)
        result = loader.load()
        
        assert result is False
    
    def test_get_features_by_id_success(self, calibration_file):
        """Test getting features by record ID."""
        loader = PixelFeaturesLoader(calibration_file=calibration_file)
        loader.load()
        
        features = loader.get_features_by_id(1)
        
        assert features is not None
        assert isinstance(features, np.ndarray)
        assert features.shape == (10,)  # 10 features
        assert features.dtype == np.float32
    
    def test_get_features_by_id_not_found(self, calibration_file):
        """Test getting features for non-existent ID."""
        loader = PixelFeaturesLoader(calibration_file=calibration_file)
        loader.load()
        
        features = loader.get_features_by_id(999)
        
        assert features is None
    
    def test_get_features_by_id_auto_load(self, calibration_file):
        """Test that get_features_by_id auto-loads if not loaded."""
        loader = PixelFeaturesLoader(calibration_file=calibration_file)
        
        # Should auto-load
        features = loader.get_features_by_id(1)
        
        assert features is not None
        assert loader._loaded is True
    
    def test_get_features_by_filename_success(self, calibration_file):
        """Test getting features by filename."""
        loader = PixelFeaturesLoader(calibration_file=calibration_file)
        loader.load()
        
        features = loader.get_features_by_filename("1.bmp")
        
        assert features is not None
        assert isinstance(features, np.ndarray)
        assert features.shape == (10,)
    
    def test_get_features_by_filename_without_extension(self, calibration_file):
        """Test getting features by filename without extension."""
        loader = PixelFeaturesLoader(calibration_file=calibration_file)
        loader.load()
        
        features = loader.get_features_by_filename("1")
        
        assert features is not None
    
    def test_get_features_by_filename_not_found(self, calibration_file):
        """Test getting features for non-existent filename."""
        loader = PixelFeaturesLoader(calibration_file=calibration_file)
        loader.load()
        
        features = loader.get_features_by_filename("nonexistent.bmp")
        
        assert features is None
    
    def test_get_all_features(self, calibration_file):
        """Test getting all features."""
        loader = PixelFeaturesLoader(calibration_file=calibration_file)
        loader.load()
        
        features_by_id, features_by_filename = loader.get_all_features()
        
        assert isinstance(features_by_id, dict)
        assert isinstance(features_by_filename, dict)
        assert len(features_by_id) == 2
        assert len(features_by_filename) == 2
    
    def test_validate_record_exists(self, calibration_file):
        """Test validating existing record."""
        loader = PixelFeaturesLoader(calibration_file=calibration_file)
        loader.load()
        
        result = loader.validate_record(record_id=1, filename="1.bmp")
        
        assert result is True
    
    def test_validate_record_id_only(self, calibration_file):
        """Test validating record by ID only."""
        loader = PixelFeaturesLoader(calibration_file=calibration_file)
        loader.load()
        
        result = loader.validate_record(record_id=1, filename=None)
        
        assert result is True
    
    def test_validate_record_not_found(self, calibration_file):
        """Test validating non-existent record."""
        loader = PixelFeaturesLoader(calibration_file=calibration_file)
        loader.load()
        
        result = loader.validate_record(record_id=999, filename=None)
        
        assert result is False
    
    def test_get_missing_records(self, calibration_file):
        """Test getting list of missing records."""
        loader = PixelFeaturesLoader(calibration_file=calibration_file)
        loader.load()
        
        missing = loader.get_missing_records([1, 2, 999, 1000])
        
        assert isinstance(missing, list)
        assert 999 in missing
        assert 1000 in missing
        assert 1 not in missing
        assert 2 not in missing
    
    def test_feature_calculation(self, calibration_file):
        """Test that features are calculated correctly."""
        loader = PixelFeaturesLoader(calibration_file=calibration_file)
        loader.load()
        
        features = loader.get_features_by_id(1)
        
        # Verify feature structure
        assert len(features) == 10
        assert all(np.isfinite(features))
        
        # Verify specific features
        # height_mm_est = height_pixels * avg_mm_per_pixel = 150.0 * 0.035 = 5.25
        assert abs(features[0] - 5.25) < 0.01
        
        # width_mm_est = width_pixels * avg_mm_per_pixel = 100.0 * 0.035 = 3.5
        assert abs(features[1] - 3.5) < 0.01
    
    def test_feature_calculation_with_zero_values(self, tmp_path):
        """Test feature calculation with zero values (should skip)."""
        calib_data = {
            "calibration_records": [
                {
                    "id": 1,
                    "filename": "1.bmp",
                    "pixel_measurements": {
                        "width_pixels": 0.0,  # Invalid
                        "height_pixels": 150.0,
                        "grain_area_pixels": 12000.0,
                        "bbox_area_pixels": 15000.0,
                        "aspect_ratio": 0.67
                    },
                    "scale_factors": {
                        "average_mm_per_pixel": 0.035
                    },
                    "background_info": {
                        "background_ratio": 0.2
                    }
                }
            ]
        }
        
        calib_file = tmp_path / "calibration.json"
        with open(calib_file, 'w', encoding='utf-8') as f:
            json.dump(calib_data, f)
        
        loader = PixelFeaturesLoader(calibration_file=calib_file)
        result = loader.load()
        
        # Should skip invalid record
        assert result is False or len(loader.features_by_id) == 0
    
    def test_reset_feature_maps(self, calibration_file):
        """Test that feature maps are reset on reload."""
        loader = PixelFeaturesLoader(calibration_file=calibration_file)
        loader.load()
        
        assert len(loader.features_by_id) == 2
        
        loader._reset_feature_maps()
        
        assert len(loader.features_by_id) == 0
        assert len(loader.features_by_filename) == 0
    
    def test_feature_names_constant(self):
        """Test that FEATURE_NAMES is defined correctly."""
        assert hasattr(PixelFeaturesLoader, 'FEATURE_NAMES')
        assert len(PixelFeaturesLoader.FEATURE_NAMES) == 10
        assert 'height_mm_est' in PixelFeaturesLoader.FEATURE_NAMES
        assert 'width_mm_est' in PixelFeaturesLoader.FEATURE_NAMES
        assert 'area_mm2_est' in PixelFeaturesLoader.FEATURE_NAMES

