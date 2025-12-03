"""
Tests for ML Regression Scalers.
"""
import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock
from pathlib import Path

from ml.regression.scalers import CacaoScalers, load_scalers, validate_scalers, create_scalers_from_data
from ml.regression.models import TARGETS


@pytest.fixture
def sample_dataframe():
    """Create sample DataFrame with target columns."""
    return pd.DataFrame({
        'alto': [20.0, 25.0, 30.0],
        'ancho': [15.0, 18.0, 20.0],
        'grosor': [10.0, 12.0, 15.0],
        'peso': [1.5, 2.0, 2.5]
    })


@pytest.fixture
def sample_dict_data():
    """Create sample dictionary data."""
    return {
        'alto': np.array([20.0, 25.0, 30.0]),
        'ancho': np.array([15.0, 18.0, 20.0]),
        'grosor': np.array([10.0, 12.0, 15.0]),
        'peso': np.array([1.5, 2.0, 2.5])
    }


class TestCacaoScalers:
    """Tests for CacaoScalers class."""

    def test_init_standard(self):
        """Test initialization with standard scaler."""
        with patch('ml.regression.scalers.ensure_dir_exists'):
            scalers = CacaoScalers(scaler_type='standard')
        
        assert scalers.scaler_type == 'standard'
        assert scalers.is_fitted is False

    def test_init_minmax(self):
        """Test initialization with minmax scaler."""
        with patch('ml.regression.scalers.ensure_dir_exists'):
            scalers = CacaoScalers(scaler_type='minmax')
        
        assert scalers.scaler_type == 'minmax'

    def test_init_robust(self):
        """Test initialization with robust scaler."""
        with patch('ml.regression.scalers.ensure_dir_exists'):
            scalers = CacaoScalers(scaler_type='robust')
        
        assert scalers.scaler_type == 'robust'

    def test_init_invalid_type(self):
        """Test initialization with invalid scaler type."""
        with patch('ml.regression.scalers.ensure_dir_exists'):
            with pytest.raises(ValueError, match='no soportado'):
                CacaoScalers(scaler_type='invalid')

    def test_fit_dataframe(self, sample_dataframe):
        """Test fitting scalers with DataFrame."""
        with patch('ml.regression.scalers.ensure_dir_exists'):
            scalers = CacaoScalers()
            scalers.fit(sample_dataframe)
        
        assert scalers.is_fitted is True
        assert len(scalers.scalers) == len(TARGETS)
        for target in TARGETS:
            assert target in scalers.scalers

    def test_fit_dict(self, sample_dict_data):
        """Test fitting scalers with dictionary."""
        with patch('ml.regression.scalers.ensure_dir_exists'):
            scalers = CacaoScalers()
            scalers.fit(sample_dict_data)
        
        assert scalers.is_fitted is True

    def test_fit_missing_target(self, sample_dataframe):
        """Test fitting with missing target."""
        with patch('ml.regression.scalers.ensure_dir_exists'):
            scalers = CacaoScalers()
            # Remove one target
            incomplete_data = sample_dataframe.drop(columns=[TARGETS[0]])
            
            with pytest.raises(ValueError, match='no encontrado'):
                scalers.fit(incomplete_data)

    def test_transform_not_fitted(self, sample_dataframe):
        """Test transform when not fitted."""
        with patch('ml.regression.scalers.ensure_dir_exists'):
            scalers = CacaoScalers()
            
            with pytest.raises(ValueError, match='deben ser ajustados'):
                scalers.transform(sample_dataframe)

    def test_transform_dataframe(self, sample_dataframe):
        """Test transforming DataFrame."""
        with patch('ml.regression.scalers.ensure_dir_exists'):
            scalers = CacaoScalers()
            scalers.fit(sample_dataframe)
            transformed = scalers.transform(sample_dataframe)
        
        assert isinstance(transformed, dict)
        for target in TARGETS:
            assert target in transformed
            assert isinstance(transformed[target], np.ndarray)

    def test_inverse_transform(self, sample_dataframe):
        """Test inverse transform."""
        with patch('ml.regression.scalers.ensure_dir_exists'):
            scalers = CacaoScalers()
            scalers.fit(sample_dataframe)
            transformed = scalers.transform(sample_dataframe)
            original = scalers.inverse_transform(transformed)
        
        assert isinstance(original, dict)
        for target in TARGETS:
            assert target in original
            # Values should be close to original (allowing for floating point errors)
            np.testing.assert_allclose(
                original[target],
                sample_dataframe[target].values,
                rtol=1e-5
            )

    def test_inverse_transform_not_fitted(self):
        """Test inverse transform when not fitted."""
        with patch('ml.regression.scalers.ensure_dir_exists'):
            scalers = CacaoScalers()
            
            with pytest.raises(ValueError, match='deben ser ajustados'):
                scalers.inverse_transform({'alto': np.array([1.0])})

    def test_fit_transform(self, sample_dataframe):
        """Test fit_transform method."""
        with patch('ml.regression.scalers.ensure_dir_exists'):
            scalers = CacaoScalers()
            transformed = scalers.fit_transform(sample_dataframe)
        
        assert scalers.is_fitted is True
        assert isinstance(transformed, dict)

    def test_apply_log_transform_grosor(self):
        """Test log transform is applied to grosor."""
        with patch('ml.regression.scalers.ensure_dir_exists'):
            scalers = CacaoScalers()
            data = np.array([10.0, 20.0, 30.0]).reshape(-1, 1)
            
            transformed = scalers._apply_log_transform('grosor', data)
            
            # Should apply log1p
            expected = np.log1p(data)
            np.testing.assert_array_almost_equal(transformed, expected)

    def test_apply_log_transform_peso(self):
        """Test log transform is applied to peso."""
        with patch('ml.regression.scalers.ensure_dir_exists'):
            scalers = CacaoScalers()
            data = np.array([1.0, 2.0, 3.0]).reshape(-1, 1)
            
            transformed = scalers._apply_log_transform('peso', data)
            
            # Should apply log1p
            expected = np.log1p(data)
            np.testing.assert_array_almost_equal(transformed, expected)

    def test_apply_log_transform_other_targets(self):
        """Test log transform is NOT applied to other targets."""
        with patch('ml.regression.scalers.ensure_dir_exists'):
            scalers = CacaoScalers()
            data = np.array([20.0, 25.0, 30.0]).reshape(-1, 1)
            
            transformed = scalers._apply_log_transform('alto', data)
            
            # Should NOT apply log1p
            np.testing.assert_array_equal(transformed, data)

    def test_save_not_fitted(self):
        """Test save when not fitted."""
        with patch('ml.regression.scalers.ensure_dir_exists'):
            scalers = CacaoScalers()
            
            with pytest.raises(ValueError, match='deben ser ajustados'):
                scalers.save()

    def test_save_success(self, sample_dataframe, tmp_path):
        """Test saving scalers."""
        with patch('ml.regression.scalers.get_regressors_artifacts_dir', return_value=tmp_path):
            with patch('ml.regression.scalers.ensure_dir_exists'):
                scalers = CacaoScalers()
                scalers.fit(sample_dataframe)
                scalers.save()
        
        # Verify files were created
        for target in TARGETS:
            scaler_path = tmp_path / f"{target}_scaler.pkl"
            assert scaler_path.exists()

    def test_load_success(self, sample_dataframe, tmp_path):
        """Test loading scalers."""
        with patch('ml.regression.scalers.get_regressors_artifacts_dir', return_value=tmp_path):
            with patch('ml.regression.scalers.ensure_dir_exists'):
                # First save
                scalers1 = CacaoScalers()
                scalers1.fit(sample_dataframe)
                scalers1.save()
                
                # Then load
                scalers2 = CacaoScalers()
                scalers2.load()
        
        assert scalers2.is_fitted is True
        assert len(scalers2.scalers) == len(TARGETS)

    def test_load_file_not_found(self, tmp_path):
        """Test loading when files don't exist."""
        with patch('ml.regression.scalers.get_regressors_artifacts_dir', return_value=tmp_path):
            with patch('ml.regression.scalers.ensure_dir_exists'):
                scalers = CacaoScalers()
                
                with pytest.raises(FileNotFoundError):
                    scalers.load()

    def test_get_scaler_stats_not_fitted(self):
        """Test get_scaler_stats when not fitted."""
        with patch('ml.regression.scalers.ensure_dir_exists'):
            scalers = CacaoScalers()
            
            with pytest.raises(ValueError, match='deben ser ajustados'):
                scalers.get_scaler_stats()

    def test_get_scaler_stats(self, sample_dataframe):
        """Test getting scaler statistics."""
        with patch('ml.regression.scalers.ensure_dir_exists'):
            scalers = CacaoScalers()
            scalers.fit(sample_dataframe)
            stats = scalers.get_scaler_stats()
        
        assert isinstance(stats, dict)
        for target in TARGETS:
            assert target in stats
            assert isinstance(stats[target], dict)


class TestScalerFunctions:
    """Tests for scaler utility functions."""

    def test_load_scalers_function(self, sample_dataframe, tmp_path):
        """Test load_scalers convenience function."""
        with patch('ml.regression.scalers.get_regressors_artifacts_dir', return_value=tmp_path):
            with patch('ml.regression.scalers.ensure_dir_exists'):
                # First save
                scalers1 = CacaoScalers()
                scalers1.fit(sample_dataframe)
                scalers1.save()
                
                # Then load using function
                scalers2 = load_scalers()
        
        assert scalers2.is_fitted is True

    def test_create_scalers_from_data(self, sample_dataframe):
        """Test create_scalers_from_data convenience function."""
        with patch('ml.regression.scalers.ensure_dir_exists'):
            scalers = create_scalers_from_data(sample_dataframe, scaler_type='standard')
        
        assert scalers.is_fitted is True
        assert scalers.scaler_type == 'standard'

    def test_validate_scalers_valid(self, sample_dataframe):
        """Test validate_scalers with valid scalers."""
        with patch('ml.regression.scalers.ensure_dir_exists'):
            scalers = CacaoScalers()
            scalers.fit(sample_dataframe)
            
            assert validate_scalers(scalers) is True

    def test_validate_scalers_not_fitted(self):
        """Test validate_scalers with unfitted scalers."""
        with patch('ml.regression.scalers.ensure_dir_exists'):
            scalers = CacaoScalers()
            
            assert validate_scalers(scalers) is False

