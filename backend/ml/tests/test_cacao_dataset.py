"""
Tests for cacao_dataset.
"""
import pytest
import numpy as np
import torch
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from ml.data.cacao_dataset import CacaoDataset


class TestCacaoDataset:
    """Tests for CacaoDataset class."""
    
    @pytest.fixture
    def mock_paths(self, tmp_path):
        """Create mock paths for testing."""
        csv_path = tmp_path / "dataset.csv"
        calibration_path = tmp_path / "calibration.json"
        crops_dir = tmp_path / "crops"
        crops_dir.mkdir()
        
        # Create mock CSV
        csv_path.write_text("id,alto,ancho,grosor,peso\n1,10.0,20.0,5.0,100.0\n")
        
        # Create mock calibration
        calibration_data = {
            "1": {
                "pixel_features": [1.0, 2.0, 3.0, 4.0]
            }
        }
        import json
        calibration_path.write_text(json.dumps(calibration_data))
        
        # Create mock image
        (crops_dir / "1.png").write_bytes(b"fake image")
        
        return {
            'csv': csv_path,
            'calibration': calibration_path,
            'crops': crops_dir
        }
    
    @patch('ml.data.cacao_dataset.CacaoDatasetLoader')
    @patch('ml.data.cacao_dataset.get_datasets_dir')
    @patch('ml.data.cacao_dataset.get_crops_dir')
    def test_initialization(self, mock_crops_dir, mock_datasets_dir, mock_loader, mock_paths):
        """Test dataset initialization."""
        mock_datasets_dir.return_value = mock_paths['calibration'].parent
        mock_crops_dir.return_value = mock_paths['crops']
        
        mock_loader_instance = Mock()
        mock_loader_instance.csv_path = mock_paths['csv']
        mock_loader.return_value = mock_loader_instance
        
        dataset = CacaoDataset(
            csv_path=mock_paths['csv'],
            calibration_file=mock_paths['calibration'],
            crops_dir=mock_paths['crops'],
            validate=False
        )
        
        assert len(dataset.records) >= 0
        assert hasattr(dataset, 'pixel_scaler')
    
    @patch('ml.data.cacao_dataset.CacaoDatasetLoader')
    @patch('ml.data.cacao_dataset.get_datasets_dir')
    @patch('ml.data.cacao_dataset.get_crops_dir')
    def test_len(self, mock_crops_dir, mock_datasets_dir, mock_loader, mock_paths):
        """Test dataset length."""
        mock_datasets_dir.return_value = mock_paths['calibration'].parent
        mock_crops_dir.return_value = mock_paths['crops']
        
        mock_loader_instance = Mock()
        mock_loader_instance.csv_path = mock_paths['csv']
        mock_loader.return_value = mock_loader_instance
        
        dataset = CacaoDataset(
            csv_path=mock_paths['csv'],
            calibration_file=mock_paths['calibration'],
            crops_dir=mock_paths['crops'],
            validate=False
        )
        
        assert isinstance(len(dataset), int)
        assert len(dataset) >= 0

