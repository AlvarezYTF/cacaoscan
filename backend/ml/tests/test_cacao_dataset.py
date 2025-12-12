"""
Tests for cacao_dataset.
"""
import pytest
import numpy as np
import torch
import json
from pathlib import Path
from PIL import Image
from unittest.mock import Mock, patch, MagicMock
from sklearn.preprocessing import StandardScaler

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
            "calibration_records": [
                {
                    "id": 1,
                    "pixel_measurements": {
                        "width_pixels": 100.0,
                        "height_pixels": 120.0,
                        "grain_area_pixels": 8000.0,
                        "bbox_area_pixels": 12000.0,
                        "aspect_ratio": 0.833
                    },
                    "scale_factors": {
                        "average_mm_per_pixel": 0.2
                    },
                    "background_info": {
                        "background_ratio": 0.1
                    }
                }
            ]
        }
        calibration_path.write_text(json.dumps(calibration_data), encoding='utf-8')
        
        # Create mock image
        image_path = crops_dir / "1.png"
        image = Image.new('RGB', (224, 224), color='red')
        image.save(image_path)
        
        return {
            'csv': csv_path,
            'calibration': calibration_path,
            'crops': crops_dir
        }
    
    @pytest.fixture
    def mock_valid_records(self):
        """Create mock valid records."""
        return [
            {
                'id': 1,
                'alto': 10.0,
                'ancho': 20.0,
                'grosor': 5.0,
                'peso': 100.0,
                'crop_image_path': '1.png'
            }
        ]
    
    @patch('ml.data.cacao_dataset.CacaoDatasetLoader')
    @patch('ml.data.cacao_dataset.get_datasets_dir')
    @patch('ml.data.cacao_dataset.get_crops_dir')
    def test_initialization(self, mock_crops_dir, mock_datasets_dir, mock_loader, mock_paths, mock_valid_records):
        """Test dataset initialization."""
        mock_datasets_dir.return_value = mock_paths['calibration'].parent
        mock_crops_dir.return_value = mock_paths['crops']
        
        mock_loader_instance = Mock()
        mock_loader_instance.csv_path = mock_paths['csv']
        mock_loader_instance.get_valid_records.return_value = mock_valid_records
        mock_loader.return_value = mock_loader_instance
        
        dataset = CacaoDataset(
            csv_path=mock_paths['csv'],
            calibration_file=mock_paths['calibration'],
            crops_dir=mock_paths['crops'],
            validate=False
        )
        
        assert len(dataset.records) > 0
        assert hasattr(dataset, 'pixel_scaler')
        assert hasattr(dataset, 'pixel_features')
    
    @patch('ml.data.cacao_dataset.CacaoDatasetLoader')
    @patch('ml.data.cacao_dataset.get_datasets_dir')
    @patch('ml.data.cacao_dataset.get_crops_dir')
    def test_len(self, mock_crops_dir, mock_datasets_dir, mock_loader, mock_paths, mock_valid_records):
        """Test dataset length."""
        mock_datasets_dir.return_value = mock_paths['calibration'].parent
        mock_crops_dir.return_value = mock_paths['crops']
        
        mock_loader_instance = Mock()
        mock_loader_instance.csv_path = mock_paths['csv']
        mock_loader_instance.get_valid_records.return_value = mock_valid_records
        mock_loader.return_value = mock_loader_instance
        
        dataset = CacaoDataset(
            csv_path=mock_paths['csv'],
            calibration_file=mock_paths['calibration'],
            crops_dir=mock_paths['crops'],
            validate=False
        )
        
        assert isinstance(len(dataset), int)
        assert len(dataset) > 0
    
    @patch('ml.data.cacao_dataset.CacaoDatasetLoader')
    @patch('ml.data.cacao_dataset.get_datasets_dir')
    @patch('ml.data.cacao_dataset.get_crops_dir')
    def test_resolve_paths(self, mock_crops_dir, mock_datasets_dir, mock_loader, mock_paths, mock_valid_records):
        """Test path resolution."""
        mock_datasets_dir.return_value = mock_paths['calibration'].parent
        mock_crops_dir.return_value = mock_paths['crops']
        
        mock_loader_instance = Mock()
        mock_loader_instance.csv_path = mock_paths['csv']
        mock_loader_instance.get_valid_records.return_value = mock_valid_records
        mock_loader.return_value = mock_loader_instance
        
        dataset = CacaoDataset(
            csv_path=mock_paths['csv'],
            calibration_file=mock_paths['calibration'],
            crops_dir=mock_paths['crops'],
            validate=False
        )
        
        assert dataset.csv_path == mock_paths['csv']
        assert dataset.calibration_file == mock_paths['calibration']
        assert dataset.crops_dir == mock_paths['crops']
    
    @patch('ml.data.cacao_dataset.CacaoDatasetLoader')
    def test_load_valid_records_empty(self, mock_loader):
        """Test loading empty valid records raises error."""
        mock_loader_instance = Mock()
        mock_loader_instance.get_valid_records.return_value = []
        mock_loader.return_value = mock_loader_instance
        
        with pytest.raises(ValueError, match="No valid records"):
            CacaoDataset(validate=False)
    
    @patch('ml.data.cacao_dataset.CacaoDatasetLoader')
    @patch('ml.data.cacao_dataset.get_datasets_dir')
    @patch('ml.data.cacao_dataset.get_crops_dir')
    def test_load_calibration_file_not_found(self, mock_crops_dir, mock_datasets_dir, mock_loader, tmp_path, mock_valid_records):
        """Test loading calibration file when file not found."""
        mock_datasets_dir.return_value = tmp_path
        mock_crops_dir.return_value = tmp_path
        
        mock_loader_instance = Mock()
        mock_loader_instance.get_valid_records.return_value = mock_valid_records
        mock_loader.return_value = mock_loader_instance
        
        with pytest.raises(FileNotFoundError):
            CacaoDataset(
                calibration_file=tmp_path / "nonexistent.json",
                validate=False
            )
    
    def test_build_pixel_feature_vector(self):
        """Test building pixel feature vector."""
        dataset = CacaoDataset.__new__(CacaoDataset)
        
        calibration_entry = {
            "pixel_measurements": {
                "width_pixels": 100.0,
                "height_pixels": 120.0,
                "grain_area_pixels": 8000.0,
                "bbox_area_pixels": 12000.0,
                "aspect_ratio": 0.833
            },
            "scale_factors": {
                "average_mm_per_pixel": 0.2
            },
            "background_info": {
                "background_ratio": 0.1
            }
        }
        
        features = dataset._build_pixel_feature_vector(calibration_entry)
        
        assert features.shape == (10,)
        assert features.dtype == np.float32
        assert np.all(np.isfinite(features))
    
    def test_build_pixel_feature_vector_zero_bbox(self):
        """Test building pixel feature vector with zero bbox area."""
        dataset = CacaoDataset.__new__(CacaoDataset)
        
        calibration_entry = {
            "pixel_measurements": {
                "width_pixels": 100.0,
                "height_pixels": 120.0,
                "grain_area_pixels": 8000.0,
                "bbox_area_pixels": 0.0,
                "aspect_ratio": 0.833
            },
            "scale_factors": {
                "average_mm_per_pixel": 0.2
            },
            "background_info": {
                "background_ratio": 0.1
            }
        }
        
        features = dataset._build_pixel_feature_vector(calibration_entry)
        
        assert features[5] == 0.0  # bbox_ratio should be 0
    
    def test_resolve_crop_path_absolute(self):
        """Test resolving absolute crop path."""
        crop_path = Path("/absolute/path/image.png")
        record = {'crop_image_path': str(crop_path)}
        
        resolved = CacaoDataset._resolve_crop_path(record, Path("/crops"))
        
        assert resolved == crop_path
    
    def test_resolve_crop_path_relative(self):
        """Test resolving relative crop path."""
        crop_path = Path("relative/image.png")
        record = {'crop_image_path': str(crop_path)}
        
        resolved = CacaoDataset._resolve_crop_path(record, Path("/crops"))
        
        assert resolved == Path("/crops/relative/image.png")
    
    @patch('ml.data.cacao_dataset.CacaoDatasetLoader')
    @patch('ml.data.cacao_dataset.get_datasets_dir')
    @patch('ml.data.cacao_dataset.get_crops_dir')
    def test_getitem(self, mock_crops_dir, mock_datasets_dir, mock_loader, mock_paths, mock_valid_records):
        """Test getting item from dataset."""
        mock_datasets_dir.return_value = mock_paths['calibration'].parent
        mock_crops_dir.return_value = mock_paths['crops']
        
        mock_loader_instance = Mock()
        mock_loader_instance.csv_path = mock_paths['csv']
        mock_loader_instance.get_valid_records.return_value = mock_valid_records
        mock_loader.return_value = mock_loader_instance
        
        dataset = CacaoDataset(
            csv_path=mock_paths['csv'],
            calibration_file=mock_paths['calibration'],
            crops_dir=mock_paths['crops'],
            validate=False
        )
        
        image_tensor, pixel_features, target_vector = dataset[0]
        
        assert isinstance(image_tensor, torch.Tensor)
        assert image_tensor.shape[0] == 3
        assert isinstance(pixel_features, torch.Tensor)
        assert isinstance(target_vector, torch.Tensor)
        assert target_vector.shape[0] == 4
    
    @patch('ml.data.cacao_dataset.CacaoDatasetLoader')
    @patch('ml.data.cacao_dataset.get_datasets_dir')
    @patch('ml.data.cacao_dataset.get_crops_dir')
    def test_getitem_image_not_rgb(self, mock_crops_dir, mock_datasets_dir, mock_loader, mock_paths, mock_valid_records):
        """Test getting item with non-RGB image."""
        mock_datasets_dir.return_value = mock_paths['calibration'].parent
        mock_crops_dir.return_value = mock_paths['crops']
        
        # Create grayscale image
        image_path = mock_paths['crops'] / "1.png"
        image = Image.new('L', (224, 224), color=128)
        image.save(image_path)
        
        mock_loader_instance = Mock()
        mock_loader_instance.csv_path = mock_paths['csv']
        mock_loader_instance.get_valid_records.return_value = mock_valid_records
        mock_loader.return_value = mock_loader_instance
        
        dataset = CacaoDataset(
            csv_path=mock_paths['csv'],
            calibration_file=mock_paths['calibration'],
            crops_dir=mock_paths['crops'],
            validate=False
        )
        
        image_tensor, _, _ = dataset[0]
        
        assert image_tensor.shape[0] == 3  # Should be converted to RGB
    
    @patch('ml.data.cacao_dataset.CacaoDatasetLoader')
    @patch('ml.data.cacao_dataset.get_datasets_dir')
    @patch('ml.data.cacao_dataset.get_crops_dir')
    def test_get_pixel_scaler(self, mock_crops_dir, mock_datasets_dir, mock_loader, mock_paths, mock_valid_records):
        """Test getting pixel scaler."""
        mock_datasets_dir.return_value = mock_paths['calibration'].parent
        mock_crops_dir.return_value = mock_paths['crops']
        
        mock_loader_instance = Mock()
        mock_loader_instance.csv_path = mock_paths['csv']
        mock_loader_instance.get_valid_records.return_value = mock_valid_records
        mock_loader.return_value = mock_loader_instance
        
        dataset = CacaoDataset(
            csv_path=mock_paths['csv'],
            calibration_file=mock_paths['calibration'],
            crops_dir=mock_paths['crops'],
            validate=False
        )
        
        scaler = dataset.get_pixel_scaler()
        
        assert isinstance(scaler, StandardScaler)
    
    @patch('ml.data.cacao_dataset.CacaoDatasetLoader')
    @patch('ml.data.cacao_dataset.get_datasets_dir')
    @patch('ml.data.cacao_dataset.get_crops_dir')
    def test_validate_min_records_too_few(self, mock_crops_dir, mock_datasets_dir, mock_loader, tmp_path):
        """Test validation with too few records."""
        mock_datasets_dir.return_value = tmp_path
        mock_crops_dir.return_value = tmp_path
        
        # Create calibration with only 5 records
        calibration_path = tmp_path / "calibration.json"
        calibration_data = {
            "calibration_records": [
                {
                    "id": i,
                    "pixel_measurements": {"width_pixels": 100.0, "height_pixels": 120.0, "grain_area_pixels": 8000.0, "bbox_area_pixels": 12000.0, "aspect_ratio": 0.833},
                    "scale_factors": {"average_mm_per_pixel": 0.2},
                    "background_info": {"background_ratio": 0.1}
                }
                for i in range(5)
            ]
        }
        calibration_path.write_text(json.dumps(calibration_data), encoding='utf-8')
        
        mock_loader_instance = Mock()
        mock_loader_instance.get_valid_records.return_value = []
        mock_loader.return_value = mock_loader_instance
        
        with pytest.raises(ValueError, match="Not enough valid records"):
            CacaoDataset(
                calibration_file=calibration_path,
                validate=False
            )
    
    @patch('ml.data.cacao_dataset.CacaoDatasetLoader')
    @patch('ml.data.cacao_dataset.get_datasets_dir')
    @patch('ml.data.cacao_dataset.get_crops_dir')
    def test_fit_pixel_scaler_provided(self, mock_crops_dir, mock_datasets_dir, mock_loader, mock_paths, mock_valid_records):
        """Test fitting pixel scaler when provided."""
        mock_datasets_dir.return_value = mock_paths['calibration'].parent
        mock_crops_dir.return_value = mock_paths['crops']
        
        mock_loader_instance = Mock()
        mock_loader_instance.csv_path = mock_paths['csv']
        mock_loader_instance.get_valid_records.return_value = mock_valid_records
        mock_loader.return_value = mock_loader_instance
        
        provided_scaler = StandardScaler()
        
        dataset = CacaoDataset(
            csv_path=mock_paths['csv'],
            calibration_file=mock_paths['calibration'],
            crops_dir=mock_paths['crops'],
            pixel_scaler=provided_scaler,
            validate=False
        )
        
        assert dataset.pixel_scaler == provided_scaler
    
    @patch('ml.data.cacao_dataset.CacaoDatasetLoader')
    @patch('ml.data.cacao_dataset.get_datasets_dir')
    @patch('ml.data.cacao_dataset.get_crops_dir')
    def test_calibration_encoding_fallback(self, mock_crops_dir, mock_datasets_dir, mock_loader, tmp_path, mock_valid_records):
        """Test loading calibration with different encodings."""
        mock_datasets_dir.return_value = tmp_path
        mock_crops_dir.return_value = tmp_path
        
        calibration_path = tmp_path / "calibration.json"
        calibration_data = {
            "calibration_records": [
                {
                    "id": 1,
                    "pixel_measurements": {"width_pixels": 100.0, "height_pixels": 120.0, "grain_area_pixels": 8000.0, "bbox_area_pixels": 12000.0, "aspect_ratio": 0.833},
                    "scale_factors": {"average_mm_per_pixel": 0.2},
                    "background_info": {"background_ratio": 0.1}
                }
            ]
        }
        # Write with latin-1 encoding
        calibration_path.write_bytes(json.dumps(calibration_data).encode('latin-1'))
        
        image_path = tmp_path / "crops" / "1.png"
        image_path.parent.mkdir(parents=True, exist_ok=True)
        image = Image.new('RGB', (224, 224), color='red')
        image.save(image_path)
        
        mock_loader_instance = Mock()
        mock_loader_instance.csv_path = tmp_path / "dataset.csv"
        mock_loader_instance.get_valid_records.return_value = mock_valid_records
        mock_loader.return_value = mock_loader_instance
        
        dataset = CacaoDataset(
            calibration_file=calibration_path,
            crops_dir=tmp_path / "crops",
            validate=False
        )
        
        assert len(dataset.records) > 0

