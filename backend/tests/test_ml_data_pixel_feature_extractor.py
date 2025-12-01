"""
Unit tests for pixel feature extractor (pixel_feature_extractor.py).
Tests PixelFeatureExtractor functionality.
"""
import pytest
import json
import numpy as np
from pathlib import Path
from unittest.mock import patch

from ml.data.pixel_feature_extractor import PixelFeatureExtractor


@pytest.fixture
def sample_calibration_data():
    """Create sample calibration data for testing."""
    return {
        "calibration_records": [
            {
                "id": 1,
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


class TestPixelFeatureExtractor:
    """Tests for PixelFeatureExtractor class."""
    
    def test_initialization_default_path(self):
        """Test initialization with default path."""
        with patch('ml.data.pixel_feature_extractor.get_datasets_dir', return_value=Path('/tmp')):
            extractor = PixelFeatureExtractor()
            
            assert extractor.calibration_file == Path('/tmp') / "pixel_calibration.json"
            assert extractor._loaded is False
            assert extractor._fitted is False
    
    def test_initialization_custom_path(self, calibration_file):
        """Test initialization with custom path."""
        extractor = PixelFeatureExtractor(calibration_file=calibration_file)
        
        assert extractor.calibration_file == calibration_file
    
    def test_initialization_custom_quantile_range(self):
        """Test initialization with custom quantile range."""
        with patch('ml.data.pixel_feature_extractor.get_datasets_dir', return_value=Path('/tmp')):
            extractor = PixelFeatureExtractor(quantile_range=(0.05, 0.95))
            
            assert extractor.quantile_range == (0.05, 0.95)
    
    def test_load_success(self, calibration_file):
        """Test successful loading of calibration data."""
        extractor = PixelFeatureExtractor(calibration_file=calibration_file)
        
        result = extractor.load()
        
        assert result is True
        assert extractor._loaded is True
        assert extractor._fitted is True
        assert len(extractor.features_by_id) == 2
    
    def test_load_file_not_found(self, tmp_path):
        """Test loading when file doesn't exist."""
        calib_file = tmp_path / "nonexistent.json"
        extractor = PixelFeatureExtractor(calibration_file=calib_file)
        
        result = extractor.load()
        
        assert result is False
        assert extractor._loaded is False
    
    def test_load_empty_records(self, tmp_path):
        """Test loading with empty calibration records."""
        calib_file = tmp_path / "empty.json"
        empty_data = {"calibration_records": []}
        
        with open(calib_file, 'w', encoding='utf-8') as f:
            json.dump(empty_data, f)
        
        extractor = PixelFeatureExtractor(calibration_file=calib_file)
        result = extractor.load()
        
        assert result is False
    
    def test_load_invalid_record(self, tmp_path):
        """Test loading with invalid record (missing required fields)."""
        calib_data = {
            "calibration_records": [
                {
                    "id": 1,
                    # Missing pixel_measurements
                }
            ]
        }
        
        calib_file = tmp_path / "invalid.json"
        with open(calib_file, 'w', encoding='utf-8') as f:
            json.dump(calib_data, f)
        
        extractor = PixelFeatureExtractor(calibration_file=calib_file)
        result = extractor.load()
        
        # Should handle gracefully
        assert result is False or len(extractor.features_by_id) == 0
    
    def test_get_features_success(self, calibration_file):
        """Test getting features for a record ID."""
        extractor = PixelFeatureExtractor(calibration_file=calibration_file)
        extractor.load()
        
        features = extractor.get_features(1)
        
        assert features is not None
        assert isinstance(features, np.ndarray)
        assert features.shape == (8,)  # 8 features
        assert features.dtype == np.float32
        assert all(np.isfinite(features))
    
    def test_get_features_not_found(self, calibration_file):
        """Test getting features for non-existent ID."""
        extractor = PixelFeatureExtractor(calibration_file=calibration_file)
        extractor.load()
        
        features = extractor.get_features(999)
        
        assert features is None
    
    def test_get_features_auto_load(self, calibration_file):
        """Test that get_features auto-loads if not loaded."""
        extractor = PixelFeatureExtractor(calibration_file=calibration_file)
        
        # Should auto-load
        features = extractor.get_features(1)
        
        assert features is not None
        assert extractor._loaded is True
    
    def test_get_feature_dim(self):
        """Test getting feature dimension."""
        with patch('ml.data.pixel_feature_extractor.get_datasets_dir', return_value=Path('/tmp')):
            extractor = PixelFeatureExtractor()
            
            dim = extractor.get_feature_dim()
            
            assert dim == 8
            assert dim == len(extractor.FEATURE_NAMES)
    
    def test_feature_calculation_area_mm2(self, calibration_file):
        """Test that area_mm2 is calculated correctly."""
        extractor = PixelFeatureExtractor(calibration_file=calibration_file)
        extractor.load()
        
        features = extractor.get_features(1)
        
        # area_mm2 = grain_area_pixels * (avg_mm_per_pixel ** 2)
        # = 12000.0 * (0.035 ** 2) = 12000.0 * 0.001225 = 14.7
        expected_area = 12000.0 * (0.035 ** 2)
        assert abs(features[0] - expected_area) < 0.1
    
    def test_feature_calculation_width_height_mm(self, calibration_file):
        """Test that width_mm and height_mm are calculated correctly."""
        extractor = PixelFeatureExtractor(calibration_file=calibration_file)
        extractor.load()
        
        features = extractor.get_features(1)
        
        # width_mm = width_pixels * avg_mm_per_pixel = 100.0 * 0.035 = 3.5
        expected_width = 100.0 * 0.035
        assert abs(features[1] - expected_width) < 0.01
        
        # height_mm = height_pixels * avg_mm_per_pixel = 150.0 * 0.035 = 5.25
        expected_height = 150.0 * 0.035
        assert abs(features[2] - expected_height) < 0.01
    
    def test_feature_calculation_perimeter_mm(self, calibration_file):
        """Test that perimeter_mm is calculated correctly."""
        extractor = PixelFeatureExtractor(calibration_file=calibration_file)
        extractor.load()
        
        features = extractor.get_features(1)
        
        # perimeter_mm = (width_pixels + height_pixels) * avg_mm_per_pixel * 2
        # = (100.0 + 150.0) * 0.035 * 2 = 250.0 * 0.07 = 17.5
        expected_perimeter = (100.0 + 150.0) * 0.035 * 2
        assert abs(features[3] - expected_perimeter) < 0.1
    
    def test_feature_normalization(self, calibration_file):
        """Test that features are normalized after loading."""
        extractor = PixelFeatureExtractor(calibration_file=calibration_file)
        extractor.load()
        
        features = extractor.get_features(1)
        
        # Normalized features should have mean close to 0 and std close to 1
        # (after RobustScaler normalization)
        assert all(np.isfinite(features))
        # Features should be in reasonable range after normalization
        assert all(abs(f) < 100 for f in features)
    
    def test_extract_record_values(self, calibration_file):
        """Test _extract_record_values method."""
        extractor = PixelFeatureExtractor(calibration_file=calibration_file)
        
        record = {
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
        }
        
        values = extractor._extract_record_values(record)
        
        assert len(values) == 7
        assert values[0] == 0.035  # avg_mm_per_pixel
        assert values[1] == 100.0  # width_pixels
        assert values[2] == 150.0  # height_pixels
    
    def test_calculate_features(self, calibration_file):
        """Test _calculate_features method."""
        extractor = PixelFeatureExtractor(calibration_file=calibration_file)
        
        features = extractor._calculate_features(
            avg_mm_per_pixel=0.035,
            width_pixels=100.0,
            height_pixels=150.0,
            grain_area_pixels=12000.0,
            bbox_area_pixels=15000.0,
            aspect_ratio=0.67,
            background_ratio=0.2
        )
        
        assert isinstance(features, np.ndarray)
        assert features.shape == (8,)
        assert features.dtype == np.float32
        assert all(np.isfinite(features))
    
    def test_process_calibration_record_valid(self, calibration_file):
        """Test processing a valid calibration record."""
        extractor = PixelFeatureExtractor(calibration_file=calibration_file)
        
        record = {
            "id": 1,
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
        }
        
        record_id, features = extractor._process_calibration_record(record)
        
        assert record_id == 1
        assert features is not None
        assert isinstance(features, np.ndarray)
    
    def test_process_calibration_record_invalid(self, calibration_file):
        """Test processing an invalid calibration record."""
        extractor = PixelFeatureExtractor(calibration_file=calibration_file)
        
        record = {
            "id": 1,
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
        
        record_id, features = extractor._process_calibration_record(record)
        
        assert record_id is None
        assert features is None
    
    def test_process_calibration_record_missing_id(self, calibration_file):
        """Test processing record with missing ID."""
        extractor = PixelFeatureExtractor(calibration_file=calibration_file)
        
        record = {
            # Missing "id"
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
        }
        
        record_id, features = extractor._process_calibration_record(record)
        
        assert record_id is None
        assert features is None
    
    def test_feature_names_constant(self):
        """Test that FEATURE_NAMES is defined correctly."""
        assert hasattr(PixelFeatureExtractor, 'FEATURE_NAMES')
        assert len(PixelFeatureExtractor.FEATURE_NAMES) == 8
        assert 'area_mm2' in PixelFeatureExtractor.FEATURE_NAMES
        assert 'width_mm' in PixelFeatureExtractor.FEATURE_NAMES
        assert 'height_mm' in PixelFeatureExtractor.FEATURE_NAMES
        assert 'perimeter_mm' in PixelFeatureExtractor.FEATURE_NAMES

