"""
Unit tests for dataset loader module (dataset_loader.py).
Tests dataset loading, validation, and record generation.
"""
import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open
import tempfile
import csv

from ml.data.dataset_loader import (
    CacaoDatasetLoader,
    load_cacao_dataset,
    get_valid_cacao_records,
    get_target_data
)


@pytest.fixture
def sample_csv_data(tmp_path):
    """Create a sample CSV file for testing."""
    csv_path = tmp_path / "dataset.csv"
    data = {
        'ID': [1, 2, 3, 4, 5],
        'ALTO': [20.0, 25.0, 30.0, 22.0, 28.0],
        'ANCHO': [12.0, 15.0, 18.0, 13.0, 16.0],
        'GROSOR': [8.0, 9.0, 10.0, 8.5, 9.5],
        'PESO': [1.5, 1.8, 2.0, 1.6, 1.9],
        'filename': ['1.bmp', '2.bmp', '3.bmp', '4.bmp', '5.bmp'],
        'image_path': ['cacao_images/raw/1.bmp', 'cacao_images/raw/2.bmp', 
                      'cacao_images/raw/3.bmp', 'cacao_images/raw/4.bmp', 
                      'cacao_images/raw/5.bmp']
    }
    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False)
    return csv_path


@pytest.fixture
def mock_media_root(tmp_path):
    """Create mock media root directory structure."""
    media_root = tmp_path / "media"
    raw_dir = media_root / "cacao_images" / "raw"
    raw_dir.mkdir(parents=True)
    
    # Create some image files
    for i in range(1, 6):
        (raw_dir / f"{i}.bmp").touch()
    
    return media_root


@pytest.fixture
def dataset_loader(sample_csv_data):
    """Create a CacaoDatasetLoader instance for testing."""
    with patch('ml.data.dataset_loader.get_raw_images_dir'), \
         patch('ml.data.dataset_loader.get_crops_dir'), \
         patch('ml.data.dataset_loader.get_missing_ids_log_path'), \
         patch('ml.data.dataset_loader.ensure_dir_exists'), \
         patch('ml.data.dataset_loader.MEDIA_ROOT', Path('/tmp')):
        return CacaoDatasetLoader(csv_path=str(sample_csv_data))


class TestCacaoDatasetLoader:
    """Tests for CacaoDatasetLoader class."""
    
    def test_loader_initialization_with_path(self, sample_csv_data):
        """Test loader initialization with explicit CSV path."""
        with patch('ml.data.dataset_loader.get_raw_images_dir'), \
             patch('ml.data.dataset_loader.get_crops_dir'), \
             patch('ml.data.dataset_loader.get_missing_ids_log_path'), \
             patch('ml.data.dataset_loader.ensure_dir_exists'), \
             patch('ml.data.dataset_loader.MEDIA_ROOT', Path('/tmp')):
            loader = CacaoDatasetLoader(csv_path=str(sample_csv_data))
            
            assert loader.csv_path == Path(sample_csv_data)
    
    def test_loader_initialization_auto_detect(self, sample_csv_data):
        """Test loader initialization with auto-detection."""
        with patch('ml.data.dataset_loader.get_datasets_dir', return_value=sample_csv_data.parent), \
             patch('ml.data.dataset_loader.get_raw_images_dir'), \
             patch('ml.data.dataset_loader.get_crops_dir'), \
             patch('ml.data.dataset_loader.get_missing_ids_log_path'), \
             patch('ml.data.dataset_loader.ensure_dir_exists'), \
             patch('ml.data.dataset_loader.MEDIA_ROOT', Path('/tmp')):
            loader = CacaoDatasetLoader(csv_path=None)
            
            assert loader.csv_path is not None
    
    def test_loader_initialization_csv_not_found(self):
        """Test loader initialization when CSV is not found."""
        with patch('ml.data.dataset_loader.get_datasets_dir', return_value=Path('/nonexistent')), \
             patch('ml.data.dataset_loader.get_raw_images_dir'), \
             patch('ml.data.dataset_loader.get_crops_dir'), \
             patch('ml.data.dataset_loader.get_missing_ids_log_path'), \
             patch('ml.data.dataset_loader.ensure_dir_exists'):
            with pytest.raises(FileNotFoundError, match="Dataset CSV no encontrado"):
                CacaoDatasetLoader(csv_path=None)
    
    def test_load_dataset_success(self, dataset_loader, sample_csv_data):
        """Test successful dataset loading."""
        df = dataset_loader.load_dataset()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 5
        assert 'id' in df.columns
        assert 'alto' in df.columns
        assert 'ancho' in df.columns
        assert 'grosor' in df.columns
        assert 'peso' in df.columns
        assert 'image_path' in df.columns
    
    def test_load_dataset_missing_columns(self, tmp_path):
        """Test loading dataset with missing required columns."""
        csv_path = tmp_path / "invalid.csv"
        invalid_data = {'ID': [1, 2], 'ALTO': [20.0, 25.0]}
        pd.DataFrame(invalid_data).to_csv(csv_path, index=False)
        
        with patch('ml.data.dataset_loader.get_raw_images_dir'), \
             patch('ml.data.dataset_loader.get_crops_dir'), \
             patch('ml.data.dataset_loader.get_missing_ids_log_path'), \
             patch('ml.data.dataset_loader.ensure_dir_exists'), \
             patch('ml.data.dataset_loader.MEDIA_ROOT', Path('/tmp')):
            loader = CacaoDatasetLoader(csv_path=str(csv_path))
            
            with pytest.raises(ValueError, match="Columnas faltantes"):
                loader.load_dataset()
    
    def test_load_dataset_handles_nulls(self, tmp_path):
        """Test that null values are handled correctly."""
        csv_path = tmp_path / "with_nulls.csv"
        data = {
            'ID': [1, 2, 3],
            'ALTO': [20.0, None, 30.0],
            'ANCHO': [12.0, 15.0, None],
            'GROSOR': [8.0, 9.0, 10.0],
            'PESO': [1.5, 1.8, 2.0]
        }
        pd.DataFrame(data).to_csv(csv_path, index=False)
        
        with patch('ml.data.dataset_loader.get_raw_images_dir'), \
             patch('ml.data.dataset_loader.get_crops_dir'), \
             patch('ml.data.dataset_loader.get_missing_ids_log_path'), \
             patch('ml.data.dataset_loader.ensure_dir_exists'), \
             patch('ml.data.dataset_loader.MEDIA_ROOT', Path('/tmp')):
            loader = CacaoDatasetLoader(csv_path=str(csv_path))
            df = loader.load_dataset()
            
            # Rows with nulls should be removed
            assert len(df) < 3
    
    def test_validate_images_exist(self, dataset_loader, sample_csv_data, mock_media_root):
        """Test image existence validation."""
        df = dataset_loader.load_dataset()
        
        with patch('ml.data.dataset_loader.MEDIA_ROOT', mock_media_root):
            valid_df, missing_ids = dataset_loader.validate_images_exist(df)
            
            assert isinstance(valid_df, pd.DataFrame)
            assert isinstance(missing_ids, list)
            assert len(valid_df) <= len(df)
    
    def test_get_valid_records(self, dataset_loader, mock_media_root):
        """Test getting valid records."""
        with patch('ml.data.dataset_loader.MEDIA_ROOT', mock_media_root), \
             patch.object(dataset_loader, 'load_dataset', return_value=pd.DataFrame({
                 'id': [1, 2, 3],
                 'alto': [20.0, 25.0, 30.0],
                 'ancho': [12.0, 15.0, 18.0],
                 'grosor': [8.0, 9.0, 10.0],
                 'peso': [1.5, 1.8, 2.0],
                 'image_path': ['cacao_images/raw/1.bmp', 'cacao_images/raw/2.bmp', 'cacao_images/raw/3.bmp']
             })), \
            patch.object(dataset_loader, 'validate_images_exist', return_value=(
                pd.DataFrame({
                    'id': [1, 2],
                    'alto': [20.0, 25.0],
                    'ancho': [12.0, 15.0],
                    'grosor': [8.0, 9.0],
                    'peso': [1.5, 1.8],
                    'image_path': ['cacao_images/raw/1.bmp', 'cacao_images/raw/2.bmp'],
                    'crop_image_path': ['cacao_images/crops/1.png', 'cacao_images/crops/2.png']
                }),
                [3]
            )):
            records = dataset_loader.get_valid_records()
            
            assert isinstance(records, list)
            assert len(records) == 2
            assert all('id' in record for record in records)
            assert all('alto' in record for record in records)
            assert all('raw_image_path' in record for record in records)
    
    def test_get_dataset_stats(self, dataset_loader, mock_media_root):
        """Test getting dataset statistics."""
        with patch('ml.data.dataset_loader.MEDIA_ROOT', mock_media_root), \
             patch.object(dataset_loader, 'load_dataset', return_value=pd.DataFrame({
                 'id': [1, 2, 3],
                 'alto': [20.0, 25.0, 30.0],
                 'ancho': [12.0, 15.0, 18.0],
                 'grosor': [8.0, 9.0, 10.0],
                 'peso': [1.5, 1.8, 2.0],
                 'image_path': ['cacao_images/raw/1.bmp', 'cacao_images/raw/2.bmp', 'cacao_images/raw/3.bmp']
             })), \
             patch.object(dataset_loader, 'validate_images_exist', return_value=(
                 pd.DataFrame({
                     'id': [1, 2],
                     'alto': [20.0, 25.0],
                     'ancho': [12.0, 15.0],
                     'grosor': [8.0, 9.0],
                     'peso': [1.5, 1.8],
                    'image_path': ['cacao_images/raw/1.bmp', 'cacao_images/raw/2.bmp'],
                    'crop_image_path': ['cacao_images/crops/1.png', 'cacao_images/crops/2.png']
                }),
                [3]
            )):
            stats = dataset_loader.get_dataset_stats()
            
            assert isinstance(stats, dict)
            assert 'total_records' in stats
            assert 'valid_records' in stats
            assert 'dimensions_stats' in stats
    
    def test_filter_by_target(self, dataset_loader):
        """Test filtering dataset by target."""
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'alto': [20.0, 25.0, None],
            'ancho': [12.0, 15.0, 18.0],
            'grosor': [8.0, 9.0, 10.0],
            'peso': [1.5, 1.8, 2.0]
        })
        
        filtered = dataset_loader.filter_by_target(df, 'alto')
        
        assert len(filtered) == 2
        assert filtered['alto'].notna().all()
    
    def test_filter_by_target_invalid(self, dataset_loader):
        """Test filtering with invalid target."""
        df = pd.DataFrame({'id': [1], 'alto': [20.0]})
        
        with pytest.raises(ValueError, match="Target inválido"):
            dataset_loader.filter_by_target(df, 'invalid_target')
    
    def test_get_target_data(self, dataset_loader, mock_media_root):
        """Test getting target data."""
        with patch('ml.data.dataset_loader.MEDIA_ROOT', mock_media_root), \
             patch.object(dataset_loader, 'load_dataset', return_value=pd.DataFrame({
                 'id': [1, 2],
                 'alto': [20.0, 25.0],
                 'ancho': [12.0, 15.0],
                 'grosor': [8.0, 9.0],
                 'peso': [1.5, 1.8],
                 'image_path': ['cacao_images/raw/1.bmp', 'cacao_images/raw/2.bmp']
             })), \
             patch.object(dataset_loader, 'validate_images_exist', return_value=(
                 pd.DataFrame({
                     'id': [1, 2],
                     'alto': [20.0, 25.0],
                     'ancho': [12.0, 15.0],
                     'grosor': [8.0, 9.0],
                     'peso': [1.5, 1.8],
                    'image_path': ['cacao_images/raw/1.bmp', 'cacao_images/raw/2.bmp'],
                    'crop_image_path': ['cacao_images/crops/1.png', 'cacao_images/crops/2.png']
                }),
                []
            )):
            target_values, records = dataset_loader.get_target_data('alto')
            
            assert isinstance(target_values, np.ndarray)
            assert len(target_values) == 2
            assert isinstance(records, list)
            assert len(records) == 2


class TestDatasetLoaderConvenienceFunctions:
    """Tests for convenience functions."""
    
    def test_load_cacao_dataset(self, sample_csv_data, mock_media_root):
        """Test load_cacao_dataset convenience function."""
        with patch('ml.data.dataset_loader.CacaoDatasetLoader') as mock_loader_class, \
             patch('ml.data.dataset_loader.MEDIA_ROOT', mock_media_root):
            mock_loader = Mock()
            mock_loader.load_dataset.return_value = pd.DataFrame({'id': [1, 2]})
            mock_loader.validate_images_exist.return_value = (
                pd.DataFrame({
                    'id': [1, 2],
                    'image_path': ['cacao_images/raw/1.bmp', 'cacao_images/raw/2.bmp'],
                    'crop_image_path': ['cacao_images/crops/1.png', 'cacao_images/crops/2.png']
                }),
                []
            )
            mock_loader_class.return_value = mock_loader
            
            df, missing_ids = load_cacao_dataset(csv_path=str(sample_csv_data))
            
            assert isinstance(df, pd.DataFrame)
            assert isinstance(missing_ids, list)
    
    def test_get_valid_cacao_records(self, sample_csv_data, mock_media_root):
        """Test get_valid_cacao_records convenience function."""
        with patch('ml.data.dataset_loader.CacaoDatasetLoader') as mock_loader_class, \
             patch('ml.data.dataset_loader.MEDIA_ROOT', mock_media_root):
            mock_loader = Mock()
            mock_loader.get_valid_records.return_value = [
                {'id': 1, 'alto': 20.0},
                {'id': 2, 'alto': 25.0}
            ]
            mock_loader_class.return_value = mock_loader
            
            records = get_valid_cacao_records(csv_path=str(sample_csv_data))
            
            assert isinstance(records, list)
            assert len(records) == 2
    
    def test_get_target_data_function(self, sample_csv_data, mock_media_root):
        """Test get_target_data convenience function."""
        with patch('ml.data.dataset_loader.CacaoDatasetLoader') as mock_loader_class, \
             patch('ml.data.dataset_loader.MEDIA_ROOT', mock_media_root):
            mock_loader = Mock()
            mock_loader.get_target_data.return_value = (
                np.array([20.0, 25.0]),
                [{'id': 1}, {'id': 2}]
            )
            mock_loader_class.return_value = mock_loader
            
            target_values, records = get_target_data('alto', csv_path=str(sample_csv_data))
            
            assert isinstance(target_values, np.ndarray)
            assert isinstance(records, list)

