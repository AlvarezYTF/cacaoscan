"""
Tests for pixel features loader.
"""
import pytest
import json
import numpy as np
from pathlib import Path
from unittest.mock import patch, MagicMock
from ml.data.pixel_features_loader import PixelFeaturesLoader


class TestPixelFeaturesLoader:
    """Tests for PixelFeaturesLoader class."""
    
    @pytest.fixture
    def temp_calibration_file(self, tmp_path):
        """Create temporary calibration file."""
        calibration_file = tmp_path / "pixel_calibration.json"
        
        calibration_data = {
            "calibration_records": [
                {
                    "id": 1,
                    "filename": "test1",
                    "pixel_measurements": {
                        "width_pixels": 100.0,
                        "height_pixels": 120.0,
                        "grain_area_pixels": 8000.0,
                        "aspect_ratio": 0.833,
                        "bbox_area_pixels": 12000.0,
                        "perimeter_pixels": 220.0
                    },
                    "scale_factors": {
                        "average_mm_per_pixel": 0.1
                    },
                    "background_info": {
                        "background_ratio": 0.2
                    }
                },
                {
                    "id": 2,
                    "filename": "test2",
                    "pixel_measurements": {
                        "width_pixels": 110.0,
                        "height_pixels": 130.0,
                        "grain_area_pixels": 9000.0,
                        "aspect_ratio": 0.846,
                        "bbox_area_pixels": 14300.0,
                        "perimeter_pixels": 240.0
                    },
                    "scale_factors": {
                        "average_mm_per_pixel": 0.1
                    },
                    "background_info": {
                        "background_ratio": 0.15
                    }
                }
            ]
        }
        
        with open(calibration_file, 'w', encoding='utf-8') as f:
            json.dump(calibration_data, f)
        
        return calibration_file
    
    def test_initialization_default_path(self):
        """Test initialization with default path."""
        with patch('ml.data.pixel_features_loader.get_datasets_dir') as mock_get_dir:
            mock_get_dir.return_value = Path("/fake/datasets")
            
            loader = PixelFeaturesLoader()
            
            assert loader.calibration_file == Path("/fake/datasets") / "pixel_calibration.json"
            assert not loader._loaded
            assert len(loader.features_by_id) == 0
    
    def test_initialization_custom_path(self, temp_calibration_file):
        """Test initialization with custom path."""
        loader = PixelFeaturesLoader(calibration_file=temp_calibration_file)
        
        assert loader.calibration_file == temp_calibration_file
        assert not loader._loaded
    
    def test_load_success(self, temp_calibration_file):
        """Test successful loading of calibration data."""
        loader = PixelFeaturesLoader(calibration_file=temp_calibration_file)
        
        result = loader.load()
        
        assert result is True
        assert loader._loaded
        assert len(loader.features_by_id) == 2
        assert len(loader.features_by_filename) == 2
    
    def test_load_file_not_found(self, tmp_path):
        """Test loading when file doesn't exist."""
        non_existent_file = tmp_path / "nonexistent.json"
        loader = PixelFeaturesLoader(calibration_file=non_existent_file)
        
        result = loader.load()
        
        assert result is False
        assert not loader._loaded
    
    def test_load_empty_records(self, tmp_path):
        """Test loading with empty calibration records."""
        calibration_file = tmp_path / "empty_calibration.json"
        calibration_data = {"calibration_records": []}
        
        with open(calibration_file, 'w', encoding='utf-8') as f:
            json.dump(calibration_data, f)
        
        loader = PixelFeaturesLoader(calibration_file=calibration_file)
        
        result = loader.load()
        
        assert result is False
    
    def test_get_features_by_id(self, temp_calibration_file):
        """Test getting features by record ID."""
        loader = PixelFeaturesLoader(calibration_file=temp_calibration_file)
        loader.load()
        
        features = loader.get_features_by_id(1)
        
        assert features is not None
        assert isinstance(features, np.ndarray)
        assert len(features) == 10  # Should have 10 features
    
    def test_get_features_by_id_not_found(self, temp_calibration_file):
        """Test getting features for non-existent ID."""
        loader = PixelFeaturesLoader(calibration_file=temp_calibration_file)
        loader.load()
        
        features = loader.get_features_by_id(999)
        
        assert features is None
    
    def test_get_features_by_id_auto_load(self, temp_calibration_file):
        """Test that get_features_by_id auto-loads if not loaded."""
        loader = PixelFeaturesLoader(calibration_file=temp_calibration_file)
        
        # Don't call load() explicitly
        features = loader.get_features_by_id(1)
        
        assert loader._loaded
        assert features is not None
    
    def test_get_features_by_filename(self, temp_calibration_file):
        """Test getting features by filename."""
        loader = PixelFeaturesLoader(calibration_file=temp_calibration_file)
        loader.load()
        
        features = loader.get_features_by_filename("test1")
        
        assert features is not None
        assert isinstance(features, np.ndarray)
    
    def test_get_features_by_filename_with_extension(self, temp_calibration_file):
        """Test getting features by filename with extension."""
        loader = PixelFeaturesLoader(calibration_file=temp_calibration_file)
        loader.load()
        
        features = loader.get_features_by_filename("test1.png")
        
        assert features is not None
    
    def test_get_features_by_filename_not_found(self, temp_calibration_file):
        """Test getting features for non-existent filename."""
        loader = PixelFeaturesLoader(calibration_file=temp_calibration_file)
        loader.load()
        
        features = loader.get_features_by_filename("nonexistent")
        
        assert features is None
    
    def test_get_all_features(self, temp_calibration_file):
        """Test getting all features."""
        loader = PixelFeaturesLoader(calibration_file=temp_calibration_file)
        loader.load()
        
        features_by_id, features_by_filename = loader.get_all_features()
        
        assert isinstance(features_by_id, dict)
        assert isinstance(features_by_filename, dict)
        assert len(features_by_id) == 2
        assert len(features_by_filename) == 2
    
    def test_get_all_features_auto_load(self, temp_calibration_file):
        """Test that get_all_features auto-loads if not loaded."""
        loader = PixelFeaturesLoader(calibration_file=temp_calibration_file)
        
        # Don't call load() explicitly
        features_by_id, features_by_filename = loader.get_all_features()
        
        assert loader._loaded
        assert len(features_by_id) > 0
    
    def test_validate_record_exists(self, temp_calibration_file):
        """Test validating existing record."""
        loader = PixelFeaturesLoader(calibration_file=temp_calibration_file)
        loader.load()
        
        result = loader.validate_record(1, "test1")
        
        assert result is True
    
    def test_validate_record_not_exists(self, temp_calibration_file):
        """Test validating non-existent record."""
        loader = PixelFeaturesLoader(calibration_file=temp_calibration_file)
        loader.load()
        
        result = loader.validate_record(999)
        
        assert result is False
    
    def test_feature_names(self):
        """Test that FEATURE_NAMES is correctly defined."""
        assert len(PixelFeaturesLoader.FEATURE_NAMES) == 10
        assert "height_mm_est" in PixelFeaturesLoader.FEATURE_NAMES
        assert "width_mm_est" in PixelFeaturesLoader.FEATURE_NAMES
        assert "area_mm2_est" in PixelFeaturesLoader.FEATURE_NAMES


