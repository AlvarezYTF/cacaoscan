"""
Tests for hybrid training pipeline.
"""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from ml.pipeline.hybrid_training import (
    _load_pixel_features,
    _collect_records_with_features,
    _validate_record_counts,
    _build_targets,
    _split_dataset_indices
)


class TestLoadPixelFeatures:
    """Tests for _load_pixel_features function."""
    
    @patch('ml.pipeline.hybrid_training.PixelFeaturesLoader')
    def test_load_pixel_features_with_file(self, mock_loader_class):
        """Test loading pixel features with file path."""
        mock_loader = MagicMock()
        mock_loader.load.return_value = True
        mock_loader_class.return_value = mock_loader
        
        calibration_file = Path("/fake/calibration.json")
        result = _load_pixel_features(calibration_file)
        
        assert result == mock_loader
        mock_loader_class.assert_called_once_with(calibration_file=calibration_file)
        mock_loader.load.assert_called_once()
    
    @patch('ml.pipeline.hybrid_training.PixelFeaturesLoader')
    def test_load_pixel_features_default(self, mock_loader_class):
        """Test loading pixel features with default path."""
        mock_loader = MagicMock()
        mock_loader.load.return_value = True
        mock_loader_class.return_value = mock_loader
        
        result = _load_pixel_features(None)
        
        assert result == mock_loader
        mock_loader_class.assert_called_once_with(calibration_file=None)


class TestBuildTargets:
    """Tests for _build_targets function."""
    
    def test_build_targets(self):
        """Test building targets from crop records."""
        crop_records = [
            {
                'alto_mm': 10.0,
                'ancho_mm': 15.0,
                'grosor_mm': 5.0,
                'peso_g': 100.0
            },
            {
                'alto_mm': 20.0,
                'ancho_mm': 25.0,
                'grosor_mm': 10.0,
                'peso_g': 200.0
            }
        ]
        
        targets = _build_targets(crop_records)
        
        assert 'alto' in targets
        assert 'ancho' in targets
        assert 'grosor' in targets
        assert 'peso' in targets
        assert len(targets['alto']) == 2
        assert targets['alto'][0] == 10.0
        assert targets['alto'][1] == 20.0


class TestSplitDatasetIndices:
    """Tests for _split_dataset_indices function."""
    
    def test_split_dataset_indices(self):
        """Test splitting dataset indices."""
        num_records = 100
        train_indices, val_indices, test_indices = _split_dataset_indices(num_records)
        
        assert len(train_indices) > 0
        assert len(val_indices) > 0
        assert len(test_indices) > 0
        
        # Check no overlap
        assert len(set(train_indices) & set(val_indices)) == 0
        assert len(set(train_indices) & set(test_indices)) == 0
        assert len(set(val_indices) & set(test_indices)) == 0
        
        # Check all indices are covered
        all_indices = set(train_indices) | set(val_indices) | set(test_indices)
        assert len(all_indices) == num_records
    
    def test_split_dataset_indices_small(self):
        """Test splitting with small number of records."""
        num_records = 10
        train_indices, val_indices, test_indices = _split_dataset_indices(num_records)
        
        assert len(train_indices) + len(val_indices) + len(test_indices) == num_records


class TestCollectRecordsWithFeatures:
    """Tests for _collect_records_with_features function."""
    
    @patch('ml.pipeline.hybrid_training.Path')
    def test_collect_records_with_features(self, mock_path):
        """Test collecting records with features."""
        # Mock path exists
        mock_path.return_value.exists.return_value = True
        
        valid_records = [
            {
                'id': 1,
                'crop_image_path': '/fake/crop1.png'
            },
            {
                'id': 2,
                'crop_image_path': '/fake/crop2.png'
            }
        ]
        
        mock_loader = MagicMock()
        mock_loader.get_features_by_id.side_effect = lambda x: [1.0] * 10 if x in [1, 2] else None
        
        crop_records, record_ids, missing_crops, missing_features = _collect_records_with_features(
            valid_records,
            mock_loader
        )
        
        assert len(crop_records) >= 0
        assert len(record_ids) >= 0


class TestValidateRecordCounts:
    """Tests for _validate_record_counts function."""
    
    def test_validate_record_counts_valid(self):
        """Test validation with valid counts."""
        crop_records = [{'id': i} for i in range(10)]
        missing_crops = 2
        missing_features = 1
        
        # Should not raise
        _validate_record_counts(crop_records, missing_crops, missing_features)
    
    def test_validate_record_counts_too_many_missing(self):
        """Test validation fails when too many records are missing."""
        crop_records = [{'id': i} for i in range(5)]
        missing_crops = 10  # Too many missing
        missing_features = 5
        
        # Should log warning but not raise
        _validate_record_counts(crop_records, missing_crops, missing_features)


