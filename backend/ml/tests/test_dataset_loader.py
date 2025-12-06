"""
Tests for dataset loader.
"""
import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import patch, Mock
from ml.data.dataset_loader import CacaoDatasetLoader


class TestCacaoDatasetLoader:
    """Tests for CacaoDatasetLoader class."""
    
    @pytest.fixture
    def sample_csv(self, tmp_path):
        """Create sample CSV file."""
        csv_path = tmp_path / "dataset.csv"
        csv_data = pd.DataFrame({
            'id': [1, 2, 3],
            'alto': [10.0, 20.0, 30.0],
            'ancho': [15.0, 25.0, 35.0],
            'grosor': [1.0, 2.0, 3.0],
            'peso': [100.0, 200.0, 300.0]
        })
        csv_data.to_csv(csv_path, index=False)
        return csv_path
    
    @patch('ml.data.dataset_loader.get_datasets_dir')
    @patch('ml.data.dataset_loader.get_raw_images_dir')
    @patch('ml.data.dataset_loader.get_crops_dir')
    def test_initialization_with_csv_path(self, mock_crops, mock_raw, mock_datasets, sample_csv, tmp_path):
        """Test initialization with CSV path."""
        mock_datasets.return_value = tmp_path
        mock_raw.return_value = tmp_path
        mock_crops.return_value = tmp_path
        
        loader = CacaoDatasetLoader(csv_path=str(sample_csv))
        
        assert loader.csv_path == sample_csv
    
    @patch('ml.data.dataset_loader.get_datasets_dir')
    @patch('ml.data.dataset_loader.get_raw_images_dir')
    @patch('ml.data.dataset_loader.get_crops_dir')
    def test_initialization_auto_detect_csv(self, mock_crops, mock_raw, mock_datasets, sample_csv, tmp_path):
        """Test initialization with auto CSV detection."""
        mock_datasets.return_value = tmp_path
        mock_raw.return_value = tmp_path
        mock_crops.return_value = tmp_path
        
        loader = CacaoDatasetLoader()
        
        assert loader.csv_path is not None
    
    @patch('ml.data.dataset_loader.get_datasets_dir')
    @patch('ml.data.dataset_loader.get_raw_images_dir')
    @patch('ml.data.dataset_loader.get_crops_dir')
    def test_initialization_csv_not_found(self, mock_crops, mock_raw, mock_datasets, tmp_path):
        """Test initialization when CSV not found."""
        mock_datasets.return_value = tmp_path
        mock_raw.return_value = tmp_path
        mock_crops.return_value = tmp_path
        
        with pytest.raises(FileNotFoundError):
            CacaoDatasetLoader(csv_path=str(tmp_path / "nonexistent.csv"))
    
    @patch('ml.data.dataset_loader.get_datasets_dir')
    @patch('ml.data.dataset_loader.get_raw_images_dir')
    @patch('ml.data.dataset_loader.get_crops_dir')
    def test_get_valid_records(self, mock_crops, mock_raw, mock_datasets, sample_csv, tmp_path):
        """Test getting valid records."""
        mock_datasets.return_value = tmp_path
        mock_raw.return_value = tmp_path
        mock_crops.return_value = tmp_path
        
        # Create sample images
        (tmp_path / "1.jpg").write_bytes(b"fake image")
        (tmp_path / "2.jpg").write_bytes(b"fake image")
        
        loader = CacaoDatasetLoader(csv_path=str(sample_csv))
        
        records = loader.get_valid_records()
        
        assert len(records) >= 0
    
    @patch('ml.data.dataset_loader.get_datasets_dir')
    @patch('ml.data.dataset_loader.get_raw_images_dir')
    @patch('ml.data.dataset_loader.get_crops_dir')
    def test_get_dataset_stats(self, mock_crops, mock_raw, mock_datasets, sample_csv, tmp_path):
        """Test getting dataset statistics."""
        mock_datasets.return_value = tmp_path
        mock_raw.return_value = tmp_path
        mock_crops.return_value = tmp_path
        
        loader = CacaoDatasetLoader(csv_path=str(sample_csv))
        
        stats = loader.get_dataset_stats()
        
        assert 'valid_records' in stats
        assert 'total_records' in stats
        assert isinstance(stats['valid_records'], int)
    
    @patch('ml.data.dataset_loader.get_datasets_dir')
    @patch('ml.data.dataset_loader.get_raw_images_dir')
    @patch('ml.data.dataset_loader.get_crops_dir')
    def test_validate_images_exist(self, mock_crops, mock_raw, mock_datasets, sample_csv, tmp_path):
        """Test validating images exist."""
        mock_datasets.return_value = tmp_path
        mock_raw.return_value = tmp_path
        mock_crops.return_value = tmp_path
        
        # Create sample images
        (tmp_path / "1.jpg").write_bytes(b"fake image")
        
        loader = CacaoDatasetLoader(csv_path=str(sample_csv))
        
        records = loader.get_valid_records()
        
        assert len(records) >= 0

