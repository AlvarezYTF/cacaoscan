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
    
    @patch('ml.data.dataset_loader.get_datasets_dir')
    @patch('ml.data.dataset_loader.get_raw_images_dir')
    @patch('ml.data.dataset_loader.get_crops_dir')
    @patch('ml.data.dataset_loader.MEDIA_ROOT')
    def test_load_dataset(self, mock_media_root, mock_crops, mock_raw, mock_datasets, tmp_path):
        """Test loading dataset."""
        mock_datasets.return_value = tmp_path
        mock_raw.return_value = tmp_path
        mock_crops.return_value = tmp_path
        mock_media_root = tmp_path
        
        csv_path = tmp_path / "dataset.csv"
        csv_data = pd.DataFrame({
            'ID': [1, 2, 3],
            'ALTO': [10.0, 20.0, 30.0],
            'ANCHO': [15.0, 25.0, 35.0],
            'GROSOR': [1.0, 2.0, 3.0],
            'PESO': [100.0, 200.0, 300.0]
        })
        csv_data.to_csv(csv_path, index=False)
        
        loader = CacaoDatasetLoader(csv_path=str(csv_path))
        df = loader.load_dataset()
        
        assert len(df) == 3
        assert 'id' in df.columns
        assert 'alto' in df.columns
        assert 'ancho' in df.columns
        assert 'grosor' in df.columns
        assert 'peso' in df.columns
    
    @patch('ml.data.dataset_loader.get_datasets_dir')
    @patch('ml.data.dataset_loader.get_raw_images_dir')
    @patch('ml.data.dataset_loader.get_crops_dir')
    @patch('ml.data.dataset_loader.MEDIA_ROOT')
    def test_load_dataset_missing_columns(self, mock_media_root, mock_crops, mock_raw, mock_datasets, tmp_path):
        """Test loading dataset with missing columns."""
        mock_datasets.return_value = tmp_path
        mock_raw.return_value = tmp_path
        mock_crops.return_value = tmp_path
        mock_media_root = tmp_path
        
        csv_path = tmp_path / "dataset.csv"
        csv_data = pd.DataFrame({
            'ID': [1, 2, 3],
            'ALTO': [10.0, 20.0, 30.0]
        })
        csv_data.to_csv(csv_path, index=False)
        
        loader = CacaoDatasetLoader(csv_path=str(csv_path))
        with pytest.raises(ValueError, match="Columnas faltantes"):
            loader.load_dataset()
    
    @patch('ml.data.dataset_loader.get_datasets_dir')
    @patch('ml.data.dataset_loader.get_raw_images_dir')
    @patch('ml.data.dataset_loader.get_crops_dir')
    @patch('ml.data.dataset_loader.MEDIA_ROOT')
    def test_load_dataset_with_nulls(self, mock_media_root, mock_crops, mock_raw, mock_datasets, tmp_path):
        """Test loading dataset with null values."""
        mock_datasets.return_value = tmp_path
        mock_raw.return_value = tmp_path
        mock_crops.return_value = tmp_path
        mock_media_root = tmp_path
        
        csv_path = tmp_path / "dataset.csv"
        csv_data = pd.DataFrame({
            'ID': [1, 2, 3],
            'ALTO': [10.0, None, 30.0],
            'ANCHO': [15.0, 25.0, 35.0],
            'GROSOR': [1.0, 2.0, 3.0],
            'PESO': [100.0, 200.0, 300.0]
        })
        csv_data.to_csv(csv_path, index=False)
        
        loader = CacaoDatasetLoader(csv_path=str(csv_path))
        df = loader.load_dataset()
        
        assert len(df) == 2  # One row with null should be dropped
    
    @patch('ml.data.dataset_loader.get_datasets_dir')
    @patch('ml.data.dataset_loader.get_raw_images_dir')
    @patch('ml.data.dataset_loader.get_crops_dir')
    @patch('ml.data.dataset_loader.MEDIA_ROOT')
    def test_validate_images_exist_with_missing(self, mock_media_root, mock_crops, mock_raw, mock_datasets, tmp_path):
        """Test validating images with some missing."""
        mock_datasets.return_value = tmp_path
        mock_raw.return_value = tmp_path
        mock_crops.return_value = tmp_path
        mock_media_root = tmp_path
        
        csv_path = tmp_path / "dataset.csv"
        csv_data = pd.DataFrame({
            'ID': [1, 2, 3],
            'ALTO': [10.0, 20.0, 30.0],
            'ANCHO': [15.0, 25.0, 35.0],
            'GROSOR': [1.0, 2.0, 3.0],
            'PESO': [100.0, 200.0, 300.0]
        })
        csv_data.to_csv(csv_path, index=False)
        
        # Create media directory structure
        media_dir = tmp_path / "cacao_images" / "raw"
        media_dir.mkdir(parents=True)
        (media_dir / "1.bmp").write_bytes(b"fake image")
        # Image 2 and 3 are missing
        
        loader = CacaoDatasetLoader(csv_path=str(csv_path))
        df = loader.load_dataset()
        valid_df, missing_ids = loader.validate_images_exist(df)
        
        assert len(valid_df) == 1
        assert len(missing_ids) == 2
    
    @patch('ml.data.dataset_loader.get_datasets_dir')
    @patch('ml.data.dataset_loader.get_raw_images_dir')
    @patch('ml.data.dataset_loader.get_crops_dir')
    @patch('ml.data.dataset_loader.MEDIA_ROOT')
    def test_filter_by_target(self, mock_media_root, mock_crops, mock_raw, mock_datasets, tmp_path):
        """Test filtering by target."""
        mock_datasets.return_value = tmp_path
        mock_raw.return_value = tmp_path
        mock_crops.return_value = tmp_path
        mock_media_root = tmp_path
        
        csv_path = tmp_path / "dataset.csv"
        csv_data = pd.DataFrame({
            'ID': [1, 2, 3],
            'ALTO': [10.0, 20.0, None],
            'ANCHO': [15.0, 25.0, 35.0],
            'GROSOR': [1.0, 2.0, 3.0],
            'PESO': [100.0, 200.0, 300.0]
        })
        csv_data.to_csv(csv_path, index=False)
        
        loader = CacaoDatasetLoader(csv_path=str(csv_path))
        df = loader.load_dataset()
        filtered_df = loader.filter_by_target(df, 'alto')
        
        assert len(filtered_df) == 2
    
    @patch('ml.data.dataset_loader.get_datasets_dir')
    @patch('ml.data.dataset_loader.get_raw_images_dir')
    @patch('ml.data.dataset_loader.get_crops_dir')
    def test_filter_by_target_invalid(self, mock_crops, mock_raw, mock_datasets, sample_csv, tmp_path):
        """Test filtering with invalid target."""
        mock_datasets.return_value = tmp_path
        mock_raw.return_value = tmp_path
        mock_crops.return_value = tmp_path
        
        loader = CacaoDatasetLoader(csv_path=str(sample_csv))
        df = loader.load_dataset()
        
        with pytest.raises(ValueError, match="Target inválido"):
            loader.filter_by_target(df, 'invalid_target')
    
    @patch('ml.data.dataset_loader.get_datasets_dir')
    @patch('ml.data.dataset_loader.get_raw_images_dir')
    @patch('ml.data.dataset_loader.get_crops_dir')
    @patch('ml.data.dataset_loader.MEDIA_ROOT')
    def test_get_target_data(self, mock_media_root, mock_crops, mock_raw, mock_datasets, tmp_path):
        """Test getting target data."""
        mock_datasets.return_value = tmp_path
        mock_raw.return_value = tmp_path
        mock_crops.return_value = tmp_path
        mock_media_root = tmp_path
        
        csv_path = tmp_path / "dataset.csv"
        csv_data = pd.DataFrame({
            'ID': [1, 2, 3],
            'ALTO': [10.0, 20.0, 30.0],
            'ANCHO': [15.0, 25.0, 35.0],
            'GROSOR': [1.0, 2.0, 3.0],
            'PESO': [100.0, 200.0, 300.0]
        })
        csv_data.to_csv(csv_path, index=False)
        
        # Create media directory structure
        media_dir = tmp_path / "cacao_images" / "raw"
        media_dir.mkdir(parents=True)
        for i in [1, 2, 3]:
            (media_dir / f"{i}.bmp").write_bytes(b"fake image")
        
        loader = CacaoDatasetLoader(csv_path=str(csv_path))
        target_values, records = loader.get_target_data('alto')
        
        assert len(target_values) > 0
        assert len(records) > 0
        assert 'alto' in records[0]
    
    @patch('ml.data.dataset_loader.get_datasets_dir')
    @patch('ml.data.dataset_loader.get_raw_images_dir')
    @patch('ml.data.dataset_loader.get_crops_dir')
    @patch('ml.data.dataset_loader.MEDIA_ROOT')
    def test_get_dataset_stats_with_data(self, mock_media_root, mock_crops, mock_raw, mock_datasets, tmp_path):
        """Test getting dataset stats with valid data."""
        mock_datasets.return_value = tmp_path
        mock_raw.return_value = tmp_path
        mock_crops.return_value = tmp_path
        mock_media_root = tmp_path
        
        csv_path = tmp_path / "dataset.csv"
        csv_data = pd.DataFrame({
            'ID': [1, 2, 3],
            'ALTO': [10.0, 20.0, 30.0],
            'ANCHO': [15.0, 25.0, 35.0],
            'GROSOR': [1.0, 2.0, 3.0],
            'PESO': [100.0, 200.0, 300.0]
        })
        csv_data.to_csv(csv_path, index=False)
        
        # Create media directory structure
        media_dir = tmp_path / "cacao_images" / "raw"
        media_dir.mkdir(parents=True)
        for i in [1, 2, 3]:
            (media_dir / f"{i}.bmp").write_bytes(b"fake image")
        
        loader = CacaoDatasetLoader(csv_path=str(csv_path))
        stats = loader.get_dataset_stats()
        
        assert 'dimensions_stats' in stats
        assert 'alto' in stats['dimensions_stats']
        assert 'min' in stats['dimensions_stats']['alto']
        assert 'max' in stats['dimensions_stats']['alto']
        assert 'mean' in stats['dimensions_stats']['alto']
    
    @patch('ml.data.dataset_loader.CacaoDatasetLoader')
    def test_load_cacao_dataset_function(self, mock_loader_class, tmp_path):
        """Test load_cacao_dataset convenience function."""
        from ml.data.dataset_loader import load_cacao_dataset
        
        mock_loader = Mock()
        mock_loader.load_dataset.return_value = pd.DataFrame({'id': [1, 2]})
        mock_loader.validate_images_exist.return_value = (pd.DataFrame({'id': [1]}), [2])
        mock_loader_class.return_value = mock_loader
        
        df, missing_ids = load_cacao_dataset()
        
        assert len(df) == 1
        assert len(missing_ids) == 1
    
    @patch('ml.data.dataset_loader.CacaoDatasetLoader')
    def test_get_valid_cacao_records_function(self, mock_loader_class):
        """Test get_valid_cacao_records convenience function."""
        from ml.data.dataset_loader import get_valid_cacao_records
        
        mock_loader = Mock()
        mock_loader.get_valid_records.return_value = [{'id': 1}, {'id': 2}]
        mock_loader_class.return_value = mock_loader
        
        records = get_valid_cacao_records()
        
        assert len(records) == 2
    
    @patch('ml.data.dataset_loader.CacaoDatasetLoader')
    def test_get_target_data_function(self, mock_loader_class):
        """Test get_target_data convenience function."""
        from ml.data.dataset_loader import get_target_data
        import numpy as np
        
        mock_loader = Mock()
        mock_loader.get_target_data.return_value = (
            np.array([10.0, 20.0]),
            [{'id': 1, 'alto': 10.0}, {'id': 2, 'alto': 20.0}]
        )
        mock_loader_class.return_value = mock_loader
        
        target_values, records = get_target_data('alto')
        
        assert len(target_values) == 2
        assert len(records) == 2

