"""
Tests for scalers utilities.
"""
import pytest
import numpy as np
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from ml.utils.scalers import CacaoRobustScaler, load_scalers


class TestCacaoRobustScaler:
    """Tests for CacaoRobustScaler class."""
    
    @pytest.fixture
    def sample_targets(self):
        """Create sample target data."""
        return {
            'alto': np.array([10.0, 20.0, 30.0, 40.0, 50.0], dtype=np.float32),
            'ancho': np.array([15.0, 25.0, 35.0, 45.0, 55.0], dtype=np.float32),
            'grosor': np.array([1.0, 2.0, 3.0, 4.0, 5.0], dtype=np.float32),
            'peso': np.array([100.0, 200.0, 300.0, 400.0, 500.0], dtype=np.float32)
        }
    
    def test_initialization(self):
        """Test scaler initialization."""
        scaler = CacaoRobustScaler()
        
        assert not scaler.is_fitted
        assert len(scaler.scalers) == 0
        assert len(scaler.TARGETS) == 4
        assert scaler.LOG_TARGETS == {'grosor', 'peso'}
    
    def test_fit(self, sample_targets):
        """Test fitting scaler."""
        scaler = CacaoRobustScaler()
        
        scaler.fit(sample_targets)
        
        assert scaler.is_fitted
        assert len(scaler.scalers) == 4
        assert all(target in scaler.scalers for target in scaler.TARGETS)
    
    def test_fit_missing_target(self, sample_targets):
        """Test fit with missing target."""
        scaler = CacaoRobustScaler()
        del sample_targets['alto']
        
        with pytest.raises(ValueError, match="Target 'alto' not found"):
            scaler.fit(sample_targets)
    
    def test_transform_without_fit(self, sample_targets):
        """Test transform without fitting."""
        scaler = CacaoRobustScaler()
        
        with pytest.raises(ValueError, match="Scalers must be fitted"):
            scaler.transform(sample_targets)
    
    def test_fit_transform(self, sample_targets):
        """Test fit_transform method."""
        scaler = CacaoRobustScaler()
        
        transformed = scaler.fit_transform(sample_targets)
        
        assert scaler.is_fitted
        assert isinstance(transformed, dict)
        assert all(target in transformed for target in scaler.TARGETS)
        assert all(isinstance(arr, np.ndarray) for arr in transformed.values())
    
    def test_transform_applies_log_to_grosor_peso(self, sample_targets):
        """Test that log transform is applied to grosor and peso."""
        scaler = CacaoRobustScaler()
        scaler.fit(sample_targets)
        
        transformed = scaler.transform(sample_targets)
        
        # Grosor and peso should have log transform applied
        # The transformed values should be different from original
        assert not np.array_equal(transformed['grosor'], sample_targets['grosor'])
        assert not np.array_equal(transformed['peso'], sample_targets['peso'])
        
        # Alto and ancho should not have log transform
        # But they will be standardized, so values will differ
    
    def test_inverse_transform(self, sample_targets):
        """Test inverse transform."""
        scaler = CacaoRobustScaler()
        scaler.fit(sample_targets)
        
        transformed = scaler.transform(sample_targets)
        denormalized = scaler.inverse_transform(transformed)
        
        assert isinstance(denormalized, dict)
        assert all(target in denormalized for target in scaler.TARGETS)
        
        # Check that inverse transform approximately recovers original values
        for target in scaler.TARGETS:
            np.testing.assert_allclose(
                denormalized[target],
                sample_targets[target],
                rtol=1e-3,
                atol=1e-3
            )
    
    def test_inverse_transform_without_fit(self, sample_targets):
        """Test inverse_transform without fitting."""
        scaler = CacaoRobustScaler()
        
        with pytest.raises(ValueError, match="Scalers must be fitted"):
            scaler.inverse_transform(sample_targets)
    
    @patch('ml.utils.scalers.get_regressors_artifacts_dir')
    @patch('ml.utils.scalers.joblib')
    def test_save(self, mock_joblib, mock_get_dir, sample_targets, tmp_path):
        """Test saving scalers."""
        mock_get_dir.return_value = tmp_path
        
        scaler = CacaoRobustScaler()
        scaler.fit(sample_targets)
        
        # Create mock files to simulate successful save
        for target in scaler.TARGETS:
            file_path = tmp_path / f"{target}_scaler.pkl"
            file_path.touch()
            file_path.write_bytes(b'test')
        
        metadata_path = tmp_path / "scaler_metadata.pkl"
        metadata_path.touch()
        metadata_path.write_bytes(b'test')
        
        scaler.save()
        
        assert mock_joblib.dump.called
    
    @patch('ml.utils.scalers.get_regressors_artifacts_dir')
    @patch('ml.utils.scalers.joblib')
    def test_save_without_fit(self, mock_joblib, mock_get_dir, tmp_path):
        """Test save without fitting."""
        mock_get_dir.return_value = tmp_path
        
        scaler = CacaoRobustScaler()
        
        with pytest.raises(ValueError, match="Scalers must be fitted"):
            scaler.save()
    
    @patch('ml.utils.scalers.get_regressors_artifacts_dir')
    @patch('ml.utils.scalers.joblib')
    def test_load(self, mock_joblib, mock_get_dir, tmp_path):
        """Test loading scalers."""
        mock_get_dir.return_value = tmp_path
        
        # Create mock scaler files
        for target in CacaoRobustScaler.TARGETS:
            file_path = tmp_path / f"{target}_scaler.pkl"
            file_path.touch()
        
        metadata_path = tmp_path / "scaler_metadata.pkl"
        metadata_path.touch()
        
        mock_joblib.load.side_effect = lambda path: MagicMock()
        
        scaler = CacaoRobustScaler()
        scaler.load()
        
        assert scaler.is_fitted
        assert len(scaler.scalers) == 4
    
    @patch('ml.utils.scalers.get_regressors_artifacts_dir')
    def test_load_missing_file(self, mock_get_dir, tmp_path):
        """Test load with missing file."""
        mock_get_dir.return_value = tmp_path
        
        scaler = CacaoRobustScaler()
        
        with pytest.raises(FileNotFoundError):
            scaler.load()
    
    @patch('ml.utils.scalers.get_regressors_artifacts_dir')
    @patch('ml.utils.scalers.joblib')
    def test_load_scalers_function(self, mock_joblib, mock_get_dir, tmp_path):
        """Test load_scalers helper function."""
        mock_get_dir.return_value = tmp_path
        
        # Create mock scaler files
        for target in CacaoRobustScaler.TARGETS:
            file_path = tmp_path / f"{target}_scaler.pkl"
            file_path.touch()
        
        metadata_path = tmp_path / "scaler_metadata.pkl"
        metadata_path.touch()
        
        mock_joblib.load.side_effect = lambda path: MagicMock()
        
        scaler = load_scalers()
        
        assert isinstance(scaler, CacaoRobustScaler)
        assert scaler.is_fitted

