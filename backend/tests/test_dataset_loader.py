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
        """Configuración antes de cada test."""
        # Mock CSV path to avoid FileNotFoundError
        with patch('ml.data.dataset_loader.get_datasets_dir') as mock_dir:
            mock_csv = Mock()
            mock_csv.exists.return_value = True
            with patch.object(CacaoDatasetLoader, '_detect_csv_file', return_value=mock_csv):
                self.loader = CacaoDatasetLoader()
    
    def test_init(self):
        """Test de inicialización."""
        assert self.loader.csv_path is not None
        assert self.loader.raw_images_dir is not None
        assert self.loader.missing_log_path is not None
    
    @patch('ml.data.dataset_loader.pd.read_csv')
    def test_load_dataset_valid_csv(self, mock_read_csv):
        """Test de carga de dataset válido."""
        # Mock de datos válidos
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
        # El código normaliza las columnas a minúsculas y agrega image_path y crop_image_path
        assert 'id' in df.columns
        assert 'alto' in df.columns
        assert 'ancho' in df.columns
        assert 'grosor' in df.columns
        assert 'peso' in df.columns
    
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
        
        # Solo debe quedar el registro sin nulos (ID 1, ya que ID 2 y 3 tienen nulos)
        assert len(df) == 1
        # El código normaliza las columnas a minúsculas
        assert df.iloc[0]['id'] == 1
    
    @patch('ml.data.dataset_loader.pd.read_csv')
    def test_load_dataset_file_not_found(self, mock_read_csv):
        """Test de carga con archivo no encontrado."""
        # Mock para que read_csv falle con FileNotFoundError
        mock_read_csv.side_effect = FileNotFoundError("File not found")
        with pytest.raises(ValueError, match="Error leyendo CSV"):
            self.loader.load_dataset()
    
    @patch('ml.data.dataset_loader.write_log')
    @patch('ml.data.dataset_loader.pd.read_csv')
    def test_validate_images_exist(self, mock_read_csv, mock_write_log):
        """Test de validación de imágenes."""
        # Mock de DataFrame con columnas en mayúsculas (se normalizan después)
        mock_data = pd.DataFrame({
            'ID': [1, 2, 3],
            'ALTO': [10.5, 11.2, 9.8],
            'ANCHO': [8.3, 8.9, 7.6],
            'GROSOR': [6.1, 6.5, 5.8],
            'PESO': [2.3, 2.5, 2.1]
        })
        mock_read_csv.return_value = mock_data
        
        # Load dataset first to get normalized columns
        with patch.object(Path, 'exists', return_value=True):
            df = self.loader.load_dataset()
        
        # Mock de existencia de archivos (solo ID 1 y 3 existen)
        original_exists = Path.exists
        def mock_exists(self_path):
            path_str = str(self_path)
            if '1.bmp' in path_str or 'raw/1' in path_str or 'cacao_images/raw/1' in path_str:
                return True
            elif '2.bmp' in path_str or 'raw/2' in path_str or 'cacao_images/raw/2' in path_str:
                return False
            elif '3.bmp' in path_str or 'raw/3' in path_str or 'cacao_images/raw/3' in path_str:
                return True
            return original_exists(self_path)
        
        with patch.object(Path, 'exists', side_effect=mock_exists, autospec=True):
            valid_df, missing_ids = self.loader.validate_images_exist(df)
        
        assert len(valid_df) == 2
        assert missing_ids == [2]
        mock_write_log.assert_called_once()
    
    def test_get_valid_records(self):
        """Test de obtención de registros válidos."""
        with patch.object(self.loader, 'load_dataset') as mock_load, \
             patch.object(self.loader, 'validate_images_exist') as mock_validate, \
             patch('ml.data.dataset_loader.get_file_timestamp') as mock_timestamp:
            
            # Mock de datos - el código normaliza las columnas a minúsculas
            mock_df = pd.DataFrame({
                'id': [1, 2],
                'alto': [10.5, 11.2],
                'ancho': [8.3, 8.9],
                'grosor': [6.1, 6.5],
                'peso': [2.3, 2.5],
                'image_path': ['raw/1.bmp', 'raw/2.bmp'],
                'crop_image_path': ['crops/1.png', 'crops/2.png']
            })
            mock_load.return_value = mock_df
            mock_validate.return_value = (mock_df, [])
            mock_timestamp.return_value = 1234567890.0
            
            # Mock de existencia de archivos
            with patch.object(Path, 'exists', return_value=True):
                records = self.loader.get_valid_records()
            
            assert len(records) == 2
            assert records[0]['id'] == 1
            assert records[0]['alto'] == pytest.approx(10.5, abs=0.01)
            assert records[0]['raw_image_path'] is not None
            assert records[0]['timestamp'] == pytest.approx(1234567890.0, abs=0.1)


