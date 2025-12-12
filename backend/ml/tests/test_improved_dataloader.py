"""
Tests for improved dataloader.
"""
import pytest
import numpy as np
import torch
from pathlib import Path
from unittest.mock import patch, MagicMock
from PIL import Image
from ml.data.improved_dataloader import (
    TargetNormalizer,
    normalize_targets,
    denormalize_predictions,
    ImprovedCacaoDataset,
    create_improved_dataloader
)


class TestTargetNormalizer:
    """Tests for TargetNormalizer class."""
    
    @pytest.fixture
    def sample_targets(self):
        """Create sample target data."""
        return {
            'alto': np.array([10.0, 20.0, 30.0], dtype=np.float32),
            'ancho': np.array([15.0, 25.0, 35.0], dtype=np.float32),
            'grosor': np.array([5.0, 10.0, 15.0], dtype=np.float32),
            'peso': np.array([100.0, 200.0, 300.0], dtype=np.float32)
        }
    
    def test_initialization_standard(self):
        """Test initialization with standard scaler."""
        normalizer = TargetNormalizer(scaler_type="standard")
        
        assert normalizer.scaler_type == "standard"
        assert not normalizer.is_fitted
        assert len(normalizer.scalers) == 0
    
    def test_initialization_minmax(self):
        """Test initialization with minmax scaler."""
        normalizer = TargetNormalizer(scaler_type="minmax")
        
        assert normalizer.scaler_type == "minmax"
    
    def test_fit(self, sample_targets):
        """Test fitting the normalizer."""
        normalizer = TargetNormalizer(scaler_type="standard")
        
        normalizer.fit(sample_targets)
        
        assert normalizer.is_fitted
        assert len(normalizer.scalers) == 4
        assert all(target in normalizer.scalers for target in normalizer.target_order)
    
    def test_fit_missing_target(self, sample_targets):
        """Test fit with missing target."""
        normalizer = TargetNormalizer(scaler_type="standard")
        del sample_targets['alto']
        
        with pytest.raises(ValueError, match="Target 'alto' no encontrado"):
            normalizer.fit(sample_targets)
    
    def test_normalize_without_fit(self, sample_targets):
        """Test normalize without fitting."""
        normalizer = TargetNormalizer(scaler_type="standard")
        
        with pytest.raises(ValueError, match="deben ser ajustados"):
            normalizer.normalize(sample_targets)
    
    def test_normalize(self, sample_targets):
        """Test normalizing targets."""
        normalizer = TargetNormalizer(scaler_type="standard")
        normalizer.fit(sample_targets)
        
        normalized = normalizer.normalize(sample_targets)
        
        assert isinstance(normalized, dict)
        assert all(target in normalized for target in normalizer.target_order)
        assert all(isinstance(arr, np.ndarray) for arr in normalized.values())
    
    def test_denormalize(self, sample_targets):
        """Test denormalizing targets."""
        normalizer = TargetNormalizer(scaler_type="standard")
        normalizer.fit(sample_targets)
        
        normalized = normalizer.normalize(sample_targets)
        denormalized = normalizer.denormalize(normalized)
        
        assert isinstance(denormalized, dict)
        # Check approximate recovery of original values
        for target in normalizer.target_order:
            np.testing.assert_allclose(
                denormalized[target],
                sample_targets[target],
                rtol=1e-3
            )
    
    def test_normalize_single(self, sample_targets):
        """Test normalizing a single value."""
        normalizer = TargetNormalizer(scaler_type="standard")
        normalizer.fit(sample_targets)
        
        normalized_value = normalizer.normalize_single('alto', 20.0)
        
        assert isinstance(normalized_value, float)
    
    def test_denormalize_single(self, sample_targets):
        """Test denormalizing a single value."""
        normalizer = TargetNormalizer(scaler_type="standard")
        normalizer.fit(sample_targets)
        
        normalized_value = normalizer.normalize_single('alto', 20.0)
        denormalized_value = normalizer.denormalize_single('alto', normalized_value)
        
        assert abs(denormalized_value - 20.0) < 1e-3


class TestNormalizeTargets:
    """Tests for normalize_targets function."""
    
    @pytest.fixture
    def sample_targets(self):
        """Create sample target data."""
        return {
            'alto': np.array([10.0, 20.0, 30.0]),
            'ancho': np.array([15.0, 25.0, 35.0]),
            'grosor': np.array([5.0, 10.0, 15.0]),
            'peso': np.array([100.0, 200.0, 300.0])
        }
    
    def test_normalize_targets_standard(self, sample_targets):
        """Test normalize_targets with standard scaler."""
        normalized, normalizer = normalize_targets(sample_targets, scaler_type="standard")
        
        assert isinstance(normalized, dict)
        assert isinstance(normalizer, TargetNormalizer)
        assert normalizer.is_fitted
        assert normalizer.scaler_type == "standard"
    
    def test_normalize_targets_minmax(self, sample_targets):
        """Test normalize_targets with minmax scaler."""
        normalized, normalizer = normalize_targets(sample_targets, scaler_type="minmax")
        
        assert isinstance(normalized, dict)
        assert normalizer.scaler_type == "minmax"


class TestDenormalizePredictions:
    """Tests for denormalize_predictions function."""
    
    def test_denormalize_predictions_dict(self):
        """Test denormalize_predictions with dict input."""
        predictions = {
            'alto': np.array([0.0, 1.0, 2.0]),
            'ancho': np.array([0.0, 1.0, 2.0])
        }
        
        normalizer = TargetNormalizer(scaler_type="standard")
        original_targets = {
            'alto': np.array([10.0, 20.0, 30.0]),
            'ancho': np.array([15.0, 25.0, 35.0]),
            'grosor': np.array([5.0, 10.0, 15.0]),
            'peso': np.array([100.0, 200.0, 300.0])
        }
        normalizer.fit(original_targets)
        
        denormalized = denormalize_predictions(predictions, normalizer)
        
        assert isinstance(denormalized, dict)
        assert 'alto' in denormalized
        assert 'ancho' in denormalized
    
    def test_denormalize_predictions_tensor(self):
        """Test denormalize_predictions with tensor input."""
        predictions = torch.tensor([[0.0, 1.0, 2.0, 3.0]])
        
        normalizer = TargetNormalizer(scaler_type="standard")
        original_targets = {
            'alto': np.array([10.0, 20.0, 30.0]),
            'ancho': np.array([15.0, 25.0, 35.0]),
            'grosor': np.array([5.0, 10.0, 15.0]),
            'peso': np.array([100.0, 200.0, 300.0])
        }
        normalizer.fit(original_targets)
        
        denormalized = denormalize_predictions(predictions, normalizer)
        
        assert isinstance(denormalized, dict)
        assert len(denormalized) == 4


@pytest.mark.skip(reason="Requires complex setup with actual dataset")
class TestImprovedCacaoDataset:
    """Tests for ImprovedCacaoDataset class."""
    
    def test_initialization(self):
        """Test dataset initialization."""
        # This would require actual image files and dataset structure
        pass


@pytest.mark.skip(reason="Requires complex setup with actual dataset")
class TestCreateImprovedDataloader:
    """Tests for create_improved_dataloader function."""
    
    def test_create_improved_dataloader(self):
        """Test creating improved dataloader."""
        # This would require actual dataset structure
        pass


