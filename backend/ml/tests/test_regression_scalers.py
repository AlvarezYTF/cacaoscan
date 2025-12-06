"""
Tests for regression scalers.
"""
import pytest
import numpy as np
import pandas as pd
from ml.regression.scalers import CacaoScalers


class TestCacaoScalers:
    """Tests for CacaoScalers class."""
    
    @pytest.fixture
    def sample_data_dict(self):
        """Create sample data as dictionary."""
        return {
            'alto': np.array([10.0, 20.0, 30.0, 40.0, 50.0], dtype=np.float32),
            'ancho': np.array([15.0, 25.0, 35.0, 45.0, 55.0], dtype=np.float32),
            'grosor': np.array([1.0, 2.0, 3.0, 4.0, 5.0], dtype=np.float32),
            'peso': np.array([100.0, 200.0, 300.0, 400.0, 500.0], dtype=np.float32)
        }
    
    @pytest.fixture
    def sample_dataframe(self):
        """Create sample data as DataFrame."""
        return pd.DataFrame({
            'alto': [10.0, 20.0, 30.0, 40.0, 50.0],
            'ancho': [15.0, 25.0, 35.0, 45.0, 55.0],
            'grosor': [1.0, 2.0, 3.0, 4.0, 5.0],
            'peso': [100.0, 200.0, 300.0, 400.0, 500.0]
        })
    
    def test_initialization_standard(self):
        """Test initialization with standard scaler."""
        scalers = CacaoScalers(scaler_type='standard')
        
        assert scalers.scaler_type == 'standard'
        assert not scalers.is_fitted
        assert len(scalers.scalers) == 0
    
    def test_initialization_minmax(self):
        """Test initialization with minmax scaler."""
        scalers = CacaoScalers(scaler_type='minmax')
        
        assert scalers.scaler_type == 'minmax'
    
    def test_initialization_robust(self):
        """Test initialization with robust scaler."""
        scalers = CacaoScalers(scaler_type='robust')
        
        assert scalers.scaler_type == 'robust'
    
    def test_initialization_invalid_type(self):
        """Test initialization with invalid scaler type."""
        with pytest.raises(ValueError, match="no soportado"):
            CacaoScalers(scaler_type='invalid')
    
    def test_fit_with_dict(self, sample_data_dict):
        """Test fitting scalers with dictionary."""
        scalers = CacaoScalers(scaler_type='standard')
        
        scalers.fit(sample_data_dict)
        
        assert scalers.is_fitted
        assert len(scalers.scalers) == 4
        assert all(target in scalers.scalers for target in ['alto', 'ancho', 'grosor', 'peso'])
    
    def test_fit_with_dataframe(self, sample_dataframe):
        """Test fitting scalers with DataFrame."""
        scalers = CacaoScalers(scaler_type='standard')
        
        scalers.fit(sample_dataframe)
        
        assert scalers.is_fitted
        assert len(scalers.scalers) == 4
    
    def test_fit_missing_target(self, sample_data_dict):
        """Test fit with missing target."""
        del sample_data_dict['alto']
        
        scalers = CacaoScalers(scaler_type='standard')
        
        with pytest.raises(ValueError, match="no encontrado"):
            scalers.fit(sample_data_dict)
    
    def test_transform_without_fit(self, sample_data_dict):
        """Test transform without fitting."""
        scalers = CacaoScalers(scaler_type='standard')
        
        with pytest.raises(ValueError, match="deben estar ajustados"):
            scalers.transform(sample_data_dict)
    
    def test_fit_transform(self, sample_data_dict):
        """Test fit_transform method."""
        scalers = CacaoScalers(scaler_type='standard')
        
        transformed = scalers.fit_transform(sample_data_dict)
        
        assert scalers.is_fitted
        assert isinstance(transformed, dict)
        assert all(target in transformed for target in ['alto', 'ancho', 'grosor', 'peso'])
    
    def test_transform_applies_log_to_grosor_peso(self, sample_data_dict):
        """Test that log transform is applied to grosor and peso."""
        scalers = CacaoScalers(scaler_type='standard')
        scalers.fit(sample_data_dict)
        
        transformed = scalers.transform(sample_data_dict)
        
        # Grosor and peso should have log transform applied
        assert not np.array_equal(transformed['grosor'], sample_data_dict['grosor'])
        assert not np.array_equal(transformed['peso'], sample_data_dict['peso'])
    
    def test_inverse_transform(self, sample_data_dict):
        """Test inverse transform."""
        scalers = CacaoScalers(scaler_type='standard')
        scalers.fit(sample_data_dict)
        
        transformed = scalers.transform(sample_data_dict)
        denormalized = scalers.inverse_transform(transformed)
        
        assert isinstance(denormalized, dict)
        assert all(target in denormalized for target in ['alto', 'ancho', 'grosor', 'peso'])
        
        # Check that inverse transform approximately recovers original values
        for target in ['alto', 'ancho', 'grosor', 'peso']:
            np.testing.assert_allclose(
                denormalized[target].flatten(),
                sample_data_dict[target],
                rtol=1e-3,
                atol=1e-3
            )
    
    def test_convert_dataframe_to_dict(self, sample_dataframe):
        """Test converting DataFrame to dictionary."""
        scalers = CacaoScalers(scaler_type='standard')
        
        result = scalers._convert_dataframe_to_dict(sample_dataframe)
        
        assert isinstance(result, dict)
        assert all(target in result for target in ['alto', 'ancho', 'grosor', 'peso'])
        assert all(arr.ndim == 2 for arr in result.values())
    
    def test_convert_dict_to_2d_arrays(self, sample_data_dict):
        """Test converting dictionary to 2D arrays."""
        scalers = CacaoScalers(scaler_type='standard')
        
        result = scalers._convert_dict_to_2d_arrays(sample_data_dict)
        
        assert isinstance(result, dict)
        assert all(arr.ndim == 2 for arr in result.values())
    
    def test_apply_log_transform_grosor(self):
        """Test applying log transform to grosor."""
        scalers = CacaoScalers(scaler_type='standard')
        data = np.array([1.0, 2.0, 3.0], dtype=np.float32).reshape(-1, 1)
        
        result = scalers._apply_log_transform('grosor', data)
        
        assert not np.array_equal(result, data)
        assert np.allclose(result, np.log1p(data))
    
    def test_apply_log_transform_alto(self):
        """Test that log transform is not applied to alto."""
        scalers = CacaoScalers(scaler_type='standard')
        data = np.array([10.0, 20.0, 30.0], dtype=np.float32).reshape(-1, 1)
        
        result = scalers._apply_log_transform('alto', data)
        
        assert np.array_equal(result, data)
    
    def test_create_scaler_standard(self):
        """Test creating standard scaler."""
        scalers = CacaoScalers(scaler_type='standard')
        
        scaler = scalers._create_scaler()
        
        from sklearn.preprocessing import StandardScaler
        assert isinstance(scaler, StandardScaler)
    
    def test_create_scaler_minmax(self):
        """Test creating minmax scaler."""
        scalers = CacaoScalers(scaler_type='minmax')
        
        scaler = scalers._create_scaler()
        
        from sklearn.preprocessing import MinMaxScaler
        assert isinstance(scaler, MinMaxScaler)
    
    def test_create_scaler_robust(self):
        """Test creating robust scaler."""
        scalers = CacaoScalers(scaler_type='robust')
        
        scaler = scalers._create_scaler()
        
        from sklearn.preprocessing import RobustScaler
        assert isinstance(scaler, RobustScaler)

