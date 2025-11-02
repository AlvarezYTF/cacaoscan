"""
Tests para el cargador de dataset.
"""
import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import Mock, patch

from ml.data.dataset_loader import CacaoDatasetLoader


class TestCacaoDatasetLoader:
    """Tests para CacaoDatasetLoader."""
    
    def setup_method(self):
        """ConfiguraciÃ³n antes de cada test."""
        self.loader = CacaoDatasetLoader()
    
    def test_init(self):
        """Test de inicializaciÃ³n."""
        assert self.loader.csv_path is not None
        assert self.loader.raw_images_dir is not None
        assert self.loader.missing_log_path is not None
    
    @patch('ml.data.dataset_loader.pd.read_csv')
    def test_load_dataset_valid_csv(self, mock_read_csv):
        """Test de carga de dataset vÃ¡lido."""
        # Mock de datos vÃ¡lidos
        mock_data = pd.DataFrame({
            'ID': [1, 2, 3],
            'ALTO': [10.5, 11.2, 9.8],
            'ANCHO': [8.3, 8.9, 7.6],
            'GROSOR': [6.1, 6.5, 5.8],
            'PESO': [2.3, 2.5, 2.1]
        })
        mock_read_csv.return_value = mock_data
        
        # Mock de que el archivo existe
        with patch.object(Path, 'exists', return_value=True):
            df = self.loader.load_dataset()
        
        assert len(df) == 3
        assert list(df.columns) == ['ID', 'ALTO', 'ANCHO', 'GROSOR', 'PESO']
        assert df['ID'].dtype == 'int64'
        assert df['ALTO'].dtype == 'float64'
    
    @patch('ml.data.dataset_loader.pd.read_csv')
    def test_load_dataset_missing_columns(self, mock_read_csv):
        """Test de carga con columnas faltantes."""
        mock_data = pd.DataFrame({
            'ID': [1, 2, 3],
            'ALTO': [10.5, 11.2, 9.8]
        })
        mock_read_csv.return_value = mock_data
        
        with patch.object(Path, 'exists', return_value=True):
            with pytest.raises(ValueError, match="Columnas faltantes"):
                self.loader.load_dataset()
    
    @patch('ml.data.dataset_loader.pd.read_csv')
    def test_load_dataset_with_nulls(self, mock_read_csv):
        """Test de carga con valores nulos."""
        mock_data = pd.DataFrame({
            'ID': [1, 2, 3],
            'ALTO': [10.5, None, 9.8],
            'ANCHO': [8.3, 8.9, None],
            'GROSOR': [6.1, 6.5, 5.8],
            'PESO': [2.3, 2.5, 2.1]
        })
        mock_read_csv.return_value = mock_data
        
        with patch.object(Path, 'exists', return_value=True):
            df = self.loader.load_dataset()
        
        # Solo debe quedar el registro sin nulos
        assert len(df) == 1
        assert df.iloc[0]['ID'] == 3
    
    def test_load_dataset_file_not_found(self):
        """Test de carga con archivo no encontrado."""
        with patch.object(Path, 'exists', return_value=False):
            with pytest.raises(FileNotFoundError):
                self.loader.load_dataset()
    
    @patch('ml.data.dataset_loader.write_log')
    def test_validate_images_exist(self, mock_write_log):
        """Test de validaciÃ³n de imÃ¡genes."""
        # Mock de DataFrame
        df = pd.DataFrame({
            'ID': [1, 2, 3],
            'ALTO': [10.5, 11.2, 9.8],
            'ANCHO': [8.3, 8.9, 7.6],
            'GROSOR': [6.1, 6.5, 5.8],
            'PESO': [2.3, 2.5, 2.1]
        })
        
        # Mock de existencia de archivos (solo ID 1 y 3 existen)
        def mock_exists(path):
            if '1.bmp' in str(path):
                return True
            elif '2.bmp' in str(path):
                return False
            elif '3.bmp' in str(path):
                return True
            return False
        
        with patch.object(Path, 'exists', side_effect=mock_exists):
            valid_df, missing_ids = self.loader.validate_images_exist(df)
        
        assert len(valid_df) == 2
        assert missing_ids == [2]
        mock_write_log.assert_called_once()
    
    def test_get_valid_records(self):
        """Test de obtenciÃ³n de registros vÃ¡lidos."""
        with patch.object(self.loader, 'load_dataset') as mock_load, \
             patch.object(self.loader, 'validate_images_exist') as mock_validate, \
             patch('ml.data.dataset_loader.get_file_timestamp') as mock_timestamp:
            
            # Mock de datos
            mock_df = pd.DataFrame({
                'ID': [1, 2],
                'ALTO': [10.5, 11.2],
                'ANCHO': [8.3, 8.9],
                'GROSOR': [6.1, 6.5],
                'PESO': [2.3, 2.5]
            })
            mock_load.return_value = mock_df
            mock_validate.return_value = (mock_df, [])
            mock_timestamp.return_value = 1234567890.0
            
            # Mock de existencia de archivos
            with patch.object(Path, 'exists', return_value=True):
                records = self.loader.get_valid_records()
            
            assert len(records) == 2
            assert records[0]['id'] == 1
            assert records[0]['alto'] == 10.5
            assert records[0]['raw_image_path'] is not None
            assert records[0]['timestamp'] == 1234567890.0


