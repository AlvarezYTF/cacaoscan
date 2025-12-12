"""
Tests for pixel feature extractor.
"""
import pytest
import json
import numpy as np
from pathlib import Path
from unittest.mock import patch, MagicMock
from ml.data.pixel_feature_extractor import PixelFeatureExtractor


class TestPixelFeatureExtractor:
    """Tests for PixelFeatureExtractor class."""
    
    @pytest.fixture
    def temp_calibration_file(self, tmp_path):
        """Create temporary calibration file."""
        calibration_file = tmp_path / "pixel_calibration.json"
        
        calibration_data = {
            "calibration_records": [
                {
                    "id": 1,
                    "pixel_measurements": {
                        "width_pixels": 100.0,
                        "height_pixels": 120.0,
                        "grain_area_pixels": 8000.0,
                        "aspect_ratio": 0.833,
                        "bbox_area_pixels": 12000.0
                    },
                    "scale_factors": {
                        "average_mm_per_pixel": 0.1
                    },
                    "background_info": {
                        "background_ratio": 0.2
                    }
                }
            ]
        }
        
        with open(calibration_file, 'w', encoding='utf-8') as f:
            json.dump(calibration_data, f)
        
        return calibration_file
    
    def test_initialization_default_path(self):
        """Test initialization with default path."""
        with patch('ml.data.pixel_feature_extractor.get_datasets_dir') as mock_get_dir:
            mock_get_dir.return_value = Path("/fake/datasets")
            
            extractor = PixelFeatureExtractor()
            
            assert extractor.calibration_file == Path("/fake/datasets") / "pixel_calibration.json"
            assert not extractor._loaded
            assert not extractor._fitted
    
    def test_initialization_custom_path(self, temp_calibration_file):
        """Test initialization with custom path."""
        extractor = PixelFeatureExtractor(calibration_file=temp_calibration_file)
        
        assert extractor.calibration_file == temp_calibration_file
    
    def test_extract_record_values(self, temp_calibration_file):
        """Test extracting values from calibration record."""
        extractor = PixelFeatureExtractor(calibration_file=temp_calibration_file)
        
        record = {
            "pixel_measurements": {
                "width_pixels": 100.0,
                "height_pixels": 120.0,
                "grain_area_pixels": 8000.0,
                "aspect_ratio": 0.833,
                "bbox_area_pixels": 12000.0
            },
            "scale_factors": {
                "average_mm_per_pixel": 0.1
            },
            "background_info": {
                "background_ratio": 0.2
            }
        }
        
        values = extractor._extract_record_values(record)
        
        assert len(values) == 7
        assert values[0] == 0.1  # average_mm_per_pixel
        assert values[1] == 100.0  # width_pixels
        assert values[2] == 120.0  # height_pixels
    
    def test_calculate_features(self, temp_calibration_file):
        """Test calculating features from pixel measurements."""
        extractor = PixelFeatureExtractor(calibration_file=temp_calibration_file)
        
        features = extractor._calculate_features(
            avg_mm_per_pixel=0.1,
            width_pixels=100.0,
            height_pixels=120.0,
            grain_area_pixels=8000.0,
            bbox_area_pixels=12000.0,
            aspect_ratio=0.833,
            background_ratio=0.2
        )
        
        assert isinstance(features, np.ndarray)
        assert len(features) == 8
        assert features[0] > 0  # area_mm2
        assert features[1] > 0  # width_mm
        assert features[2] > 0  # height_mm
    
    def test_calculate_features_zero_bbox_area(self, temp_calibration_file):
        """Test calculating features with zero bbox area."""
        extractor = PixelFeatureExtractor(calibration_file=temp_calibration_file)
        
        features = extractor._calculate_features(
            avg_mm_per_pixel=0.1,
            width_pixels=100.0,
            height_pixels=120.0,
            grain_area_pixels=8000.0,
            bbox_area_pixels=0.0,  # Zero bbox area
            aspect_ratio=0.833,
            background_ratio=0.2
        )
        
        assert isinstance(features, np.ndarray)
        assert features[5] == 0.0  # bbox_to_area_ratio should be 0
    
    def test_process_calibration_record_valid(self, temp_calibration_file):
        """Test processing valid calibration record."""
        extractor = PixelFeatureExtractor(calibration_file=temp_calibration_file)
        
        record = {
            "id": 1,
            "pixel_measurements": {
                "width_pixels": 100.0,
                "height_pixels": 120.0,
                "grain_area_pixels": 8000.0,
                "aspect_ratio": 0.833,
                "bbox_area_pixels": 12000.0
            },
            "scale_factors": {
                "average_mm_per_pixel": 0.1
            },
            "background_info": {
                "background_ratio": 0.2
            }
        }
        
        record_id, features = extractor._process_calibration_record(record)
        
        assert record_id == 1
        assert features is not None
        assert isinstance(features, np.ndarray)
    
    def test_process_calibration_record_invalid_measurements(self, temp_calibration_file):
        """Test processing record with invalid measurements."""
        extractor = PixelFeatureExtractor(calibration_file=temp_calibration_file)
        
        record = {
            "id": 1,
            "pixel_measurements": {
                "width_pixels": 0.0,  # Invalid: zero width
                "height_pixels": 120.0,
                "grain_area_pixels": 8000.0,
                "aspect_ratio": 0.833,
                "bbox_area_pixels": 12000.0
            },
            "scale_factors": {
                "average_mm_per_pixel": 0.1
            },
            "background_info": {
                "background_ratio": 0.2
            }
        }
        
        record_id, features = extractor._process_calibration_record(record)
        
        assert record_id is None
        assert features is None
    
    def test_process_calibration_record_missing_fields(self, temp_calibration_file):
        """Test processing record with missing fields."""
        extractor = PixelFeatureExtractor(calibration_file=temp_calibration_file)
        
        record = {
            "id": 1,
            # Missing required fields
        }
        
        record_id, features = extractor._process_calibration_record(record)
        
        assert record_id is None
        assert features is None
    
    def test_load_success(self, temp_calibration_file):
        """Test successful loading of calibration data."""
        extractor = PixelFeatureExtractor(calibration_file=temp_calibration_file)
        
        result = extractor.load()
        
        assert result is True
        assert extractor._loaded
        assert len(extractor.features_by_id) > 0
    
    def test_load_file_not_found(self, tmp_path):
        """Test loading when file doesn't exist."""
        non_existent_file = tmp_path / "nonexistent.json"
        extractor = PixelFeatureExtractor(calibration_file=non_existent_file)
        
        result = extractor.load()
        
        assert result is False
        assert not extractor._loaded
    
    def test_fit(self, temp_calibration_file):
        """Test fitting the scaler."""
        extractor = PixelFeatureExtractor(calibration_file=temp_calibration_file)
        extractor.load()
        
        extractor.fit()
        
        assert extractor._fitted
        assert extractor.scaler is not None
    
    def test_get_features_by_id(self, temp_calibration_file):
        """Test getting features by record ID."""
        extractor = PixelFeatureExtractor(calibration_file=temp_calibration_file)
        extractor.load()
        extractor.fit()
        
        features = extractor.get_features_by_id(1)
        
        assert features is not None
        assert isinstance(features, np.ndarray)
        assert len(features) == 8
    
    def test_get_features_by_id_normalized(self, temp_calibration_file):
        """Test getting normalized features."""
        extractor = PixelFeatureExtractor(calibration_file=temp_calibration_file)
        extractor.load()
        extractor.fit()
        
        features_normalized = extractor.get_features_by_id(1, normalized=True)
        features_raw = extractor.get_features_by_id(1, normalized=False)
        
        assert features_normalized is not None
        assert features_raw is not None
        # Normalized features should be different from raw
        assert not np.array_equal(features_normalized, features_raw)
    
    def test_feature_names(self):
        """Test that FEATURE_NAMES is correctly defined."""
        assert len(PixelFeatureExtractor.FEATURE_NAMES) == 8
        assert "area_mm2" in PixelFeatureExtractor.FEATURE_NAMES
        assert "width_mm" in PixelFeatureExtractor.FEATURE_NAMES
        assert "height_mm" in PixelFeatureExtractor.FEATURE_NAMES


