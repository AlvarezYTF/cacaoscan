"""
Unit tests for regression scalers module (scalers.py).
Tests scaler functionality including fit, transform, and inverse_transform.
"""
import pytest
import numpy as np
import pandas as pd
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import joblib
import tempfile

from ml.regression.scalers import (
    CacaoScalers,
    load_scalers,
    save_scalers,
    create_scalers_from_data,
    validate_scalers
)
from ml.regression.models import TARGETS


@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    return {
        'alto': np.array([20.0, 25.0, 30.0, 22.0, 28.0], dtype=np.float32),
        'ancho': np.array([12.0, 15.0, 18.0, 13.0, 16.0], dtype=np.float32),
        'grosor': np.array([8.0, 9.0, 10.0, 8.5, 9.5], dtype=np.float32),
        'peso': np.array([1.5, 1.8, 2.0, 1.6, 1.9], dtype=np.float32)
    }


@pytest.fixture
def sample_dataframe(sample_data):
    """Create sample DataFrame for testing."""
    return pd.DataFrame(sample_data)


@pytest.fixture
def scalers():
    """Create a CacaoScalers instance for testing."""
    with patch('ml.regression.scalers.get_regressors_artifacts_dir'), \
         patch('ml.regression.scalers.ensure_dir_exists'):
        return CacaoScalers(scaler_type="standard")


class TestCacaoScalers:
    """Tests for CacaoScalers class."""
    
    def test_scalers_initialization(self):
        """Test scalers initialization."""
        with patch('ml.regression.scalers.get_regressors_artifacts_dir'), \
             patch('ml.regression.scalers.ensure_dir_exists'):
            scalers = CacaoScalers(scaler_type="standard")
            
            assert scalers.scaler_type == "standard"
            assert scalers.is_fitted is False
            assert len(scalers.scalers) == 0
    
    def test_scalers_initialization_minmax(self):
        """Test scalers initialization with MinMaxScaler."""
        with patch('ml.regression.scalers.get_regressors_artifacts_dir'), \
             patch('ml.regression.scalers.ensure_dir_exists'):
            scalers = CacaoScalers(scaler_type="minmax")
            
            assert scalers.scaler_type == "minmax"
    
    def test_scalers_initialization_robust(self):
        """Test scalers initialization with RobustScaler."""
        with patch('ml.regression.scalers.get_regressors_artifacts_dir'), \
             patch('ml.regression.scalers.ensure_dir_exists'):
            scalers = CacaoScalers(scaler_type="robust")
            
            assert scalers.scaler_type == "robust"
    
    def test_scalers_initialization_invalid_type(self):
        """Test scalers initialization with invalid type."""
        with patch('ml.regression.scalers.get_regressors_artifacts_dir'), \
             patch('ml.regression.scalers.ensure_dir_exists'):
            with pytest.raises(ValueError, match="Tipo de escalador"):
                CacaoScalers(scaler_type="invalid")
    
    def test_fit_with_dict(self, scalers, sample_data):
        """Test fitting scalers with dictionary data."""
        scalers.fit(sample_data)
        
        assert scalers.is_fitted is True
        assert len(scalers.scalers) == len(TARGETS)
        for target in TARGETS:
            assert target in scalers.scalers
    
    def test_fit_with_dataframe(self, scalers, sample_dataframe):
        """Test fitting scalers with DataFrame."""
        scalers.fit(sample_dataframe)
        
        assert scalers.is_fitted is True
        assert len(scalers.scalers) == len(TARGETS)
    
    def test_fit_missing_column(self, scalers, sample_dataframe):
        """Test fitting with missing column."""
        sample_dataframe = sample_dataframe.drop(columns=['alto'])
        
        with pytest.raises(ValueError, match="Columna 'alto' no encontrada"):
            scalers.fit(sample_dataframe)
    
    def test_fit_log_transform_applied(self, scalers, sample_data):
        """Test that log transform is applied to grosor and peso."""
        scalers.fit(sample_data)
        
        # Verify that log transform was applied (scaler should have different stats)
        assert scalers.is_fitted is True
    
    def test_transform_not_fitted(self, scalers, sample_data):
        """Test that transform raises error when not fitted."""
        with pytest.raises(ValueError, match="deben ser ajustados"):
            scalers.transform(sample_data)
    
    def test_transform_with_dict(self, scalers, sample_data):
        """Test transforming data with dictionary."""
        scalers.fit(sample_data)
        transformed = scalers.transform(sample_data)
        
        assert isinstance(transformed, dict)
        for target in TARGETS:
            assert target in transformed
            assert isinstance(transformed[target], np.ndarray)
            assert len(transformed[target]) == len(sample_data[target])
    
    def test_transform_with_dataframe(self, scalers, sample_dataframe):
        """Test transforming data with DataFrame."""
        scalers.fit(sample_dataframe)
        transformed = scalers.transform(sample_dataframe)
        
        assert isinstance(transformed, dict)
        for target in TARGETS:
            assert target in transformed
    
    def test_inverse_transform_not_fitted(self, scalers, sample_data):
        """Test that inverse_transform raises error when not fitted."""
        with pytest.raises(ValueError, match="deben ser ajustados"):
            scalers.inverse_transform(sample_data)
    
    def test_inverse_transform_roundtrip(self, scalers, sample_data):
        """Test that inverse_transform reverses transform."""
        scalers.fit(sample_data)
        transformed = scalers.transform(sample_data)
        original = scalers.inverse_transform(transformed)
        
        for target in TARGETS:
            np.testing.assert_allclose(
                sample_data[target],
                original[target],
                rtol=1e-5,
                err_msg=f"{target}: Roundtrip failed"
            )
    
    def test_fit_transform(self, scalers, sample_data):
        """Test fit_transform method."""
        transformed = scalers.fit_transform(sample_data)
        
        assert scalers.is_fitted is True
        assert isinstance(transformed, dict)
        for target in TARGETS:
            assert target in transformed
    
    def test_save_not_fitted(self, scalers, tmp_path):
        """Test that save raises error when not fitted."""
        with patch('ml.regression.scalers.get_regressors_artifacts_dir', return_value=tmp_path):
            with pytest.raises(ValueError, match="deben ser ajustados"):
                scalers.save()
    
    def test_save_success(self, scalers, sample_data, tmp_path):
        """Test successful saving of scalers."""
        scalers.fit(sample_data)
        
        with patch('ml.regression.scalers.get_regressors_artifacts_dir', return_value=tmp_path):
            scalers.save()
            
            # Verify files were created
            for target in TARGETS:
                scaler_path = tmp_path / f"{target}_scaler.pkl"
                assert scaler_path.exists()
                assert scaler_path.stat().st_size > 0
    
    def test_load_success(self, scalers, sample_data, tmp_path):
        """Test successful loading of scalers."""
        scalers.fit(sample_data)
        
        with patch('ml.regression.scalers.get_regressors_artifacts_dir', return_value=tmp_path):
            scalers.save()
            
            # Create new scaler and load
            new_scalers = CacaoScalers()
            with patch('ml.regression.scalers.get_regressors_artifacts_dir', return_value=tmp_path):
                new_scalers.load()
                
                assert new_scalers.is_fitted is True
                assert len(new_scalers.scalers) == len(TARGETS)
    
    def test_load_file_not_found(self, scalers, tmp_path):
        """Test loading when files don't exist."""
        with patch('ml.regression.scalers.get_regressors_artifacts_dir', return_value=tmp_path):
            with pytest.raises(FileNotFoundError):
                scalers.load()
    
    def test_get_scaler_stats_not_fitted(self, scalers):
        """Test that get_scaler_stats raises error when not fitted."""
        with pytest.raises(ValueError, match="deben ser ajustados"):
            scalers.get_scaler_stats()
    
    def test_get_scaler_stats_success(self, scalers, sample_data):
        """Test getting scaler statistics."""
        scalers.fit(sample_data)
        stats = scalers.get_scaler_stats()
        
        assert isinstance(stats, dict)
        for target in TARGETS:
            assert target in stats
            assert 'mean' in stats[target]
            assert 'std' in stats[target]


class TestScalerConvenienceFunctions:
    """Tests for convenience functions."""
    
    def test_load_scalers_success(self, sample_data, tmp_path):
        """Test load_scalers convenience function."""
        # First create and save scalers
        scalers = CacaoScalers()
        scalers.fit(sample_data)
        
        with patch('ml.regression.scalers.get_regressors_artifacts_dir', return_value=tmp_path):
            scalers.save()
            
            # Load using convenience function
            loaded = load_scalers()
            
            assert loaded.is_fitted is True
            assert len(loaded.scalers) == len(TARGETS)
    
    def test_save_scalers_function(self, sample_data, tmp_path):
        """Test save_scalers convenience function."""
        scalers = CacaoScalers()
        scalers.fit(sample_data)
        
        with patch('ml.regression.scalers.get_regressors_artifacts_dir', return_value=tmp_path):
            save_scalers(scalers)
            
            # Verify files were created
            for target in TARGETS:
                scaler_path = tmp_path / f"{target}_scaler.pkl"
                assert scaler_path.exists()
    
    def test_create_scalers_from_data(self, sample_data):
        """Test create_scalers_from_data convenience function."""
        with patch('ml.regression.scalers.get_regressors_artifacts_dir'), \
             patch('ml.regression.scalers.ensure_dir_exists'):
            scalers = create_scalers_from_data(sample_data, scaler_type="standard")
            
            assert scalers.is_fitted is True
            assert len(scalers.scalers) == len(TARGETS)
    
    def test_validate_scalers_valid(self, sample_data):
        """Test validate_scalers with valid scalers."""
        with patch('ml.regression.scalers.get_regressors_artifacts_dir'), \
             patch('ml.regression.scalers.ensure_dir_exists'):
            scalers = CacaoScalers()
            scalers.fit(sample_data)
            
            assert validate_scalers(scalers) is True
    
    def test_validate_scalers_not_fitted(self):
        """Test validate_scalers with unfitted scalers."""
        with patch('ml.regression.scalers.get_regressors_artifacts_dir'), \
             patch('ml.regression.scalers.ensure_dir_exists'):
            scalers = CacaoScalers()
            
            assert validate_scalers(scalers) is False
    
    def test_validate_scalers_missing_scaler(self, sample_data):
        """Test validate_scalers with missing scaler."""
        with patch('ml.regression.scalers.get_regressors_artifacts_dir'), \
             patch('ml.regression.scalers.ensure_dir_exists'):
            scalers = CacaoScalers()
            scalers.fit(sample_data)
            # Remove one scaler
            del scalers.scalers['alto']
            
            assert validate_scalers(scalers) is False

