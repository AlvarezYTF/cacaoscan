"""
Unit tests for train_cacao_models command module (train_cacao_models.py).
Tests Django management command for training cacao regression models.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock, call
from django.core.management.base import CommandError
from pathlib import Path

from training.management.commands.train_cacao_models import Command


@pytest.fixture
def command():
    """Create a Command instance for testing."""
    return Command()


@pytest.fixture
def mock_options():
    """Create mock command options."""
    return {
        'multihead': False,
        'model_type': 'resnet18',
        'hybrid': False,
        'hybrid_v2': False,
        'use_pixel_features': True,
        'use_mixed_precision': False,
        'epochs': 50,
        'batch_size': 32,
        'img_size': 224,
        'learning_rate': 1e-4,
        'loss_type': 'smooth_l1',
        'scheduler_type': 'cosine_warmup',
        'early_stopping_patience': 15,
        'dropout_rate': 0.25,
        'num_workers': 0,
        'targets': 'all',
        'validate_only': False,
        'test_mode': False,
        'use_raw_images': False,
        'segmentation_backend': 'auto',
        'train_separate_dimensions': False,
        'max_grad_norm': 1.0,
        'warmup_epochs': None
    }


class TestTrainCacaoModelsCommand:
    """Tests for train_cacao_models Command class."""
    
    def test_command_initialization(self):
        """Test command initialization."""
        cmd = Command()
        assert cmd is not None
    
    def test_parse_targets_all(self, command):
        """Test parsing 'all' targets."""
        targets = command._parse_targets('all')
        
        assert targets == ['alto', 'ancho', 'grosor', 'peso']
    
    def test_parse_targets_specific(self, command):
        """Test parsing specific targets."""
        targets = command._parse_targets('alto,peso')
        
        assert targets == ['alto', 'peso']
    
    def test_parse_targets_invalid(self, command):
        """Test parsing invalid target."""
        with pytest.raises(ValueError, match="Target inválido"):
            command._parse_targets('invalid_target')
    
    def test_parse_targets_case_insensitive(self, command):
        """Test that target parsing is case insensitive."""
        targets = command._parse_targets('ALTO,Ancho')
        
        assert targets == ['alto', 'ancho']
    
    @patch('ml.data.dataset_loader.CacaoDatasetLoader')
    @patch('training.management.commands.train_cacao_models.get_raw_images_dir')
    def test_validate_config_success(self, mock_get_raw_dir, mock_loader_class, command, tmp_path):
        """Test successful configuration validation."""
        mock_raw_dir = tmp_path / "raw_images"
        mock_raw_dir.mkdir()
        # Need at least 10 files
        for i in range(15):
            (mock_raw_dir / f"image{i}.bmp").touch()
        mock_get_raw_dir.return_value = mock_raw_dir
        
        mock_loader = Mock()
        mock_loader.load_dataset.return_value = Mock(__len__=Mock(return_value=20))
        mock_loader.get_valid_records.return_value = [{'id': i} for i in range(15)]
        mock_loader_class.return_value = mock_loader
        
        config = {
            'model_type': 'resnet18',
            'epochs': 50,
            'batch_size': 32,
            'learning_rate': 1e-4,
            'hybrid': False
        }
        
        # Should not raise
        command._validate_config(config)
    
    @patch('training.management.commands.train_cacao_models.get_raw_images_dir')
    def test_validate_config_raw_dir_not_found(self, mock_get_raw_dir, command):
        """Test validation when raw images directory doesn't exist."""
        mock_get_raw_dir.return_value = Path("/nonexistent")
        
        config = {'model_type': 'resnet18'}
        
        with pytest.raises(CommandError, match="Directorio de imágenes raw no encontrado"):
            command._validate_config(config)
    
    @patch('training.management.commands.train_cacao_models.get_raw_images_dir')
    def test_validate_config_too_few_raw_images(self, mock_get_raw_dir, command, tmp_path):
        """Test validation when too few raw images."""
        mock_raw_dir = tmp_path / "raw_images"
        mock_raw_dir.mkdir()
        (mock_raw_dir / "image1.bmp").touch()
        mock_get_raw_dir.return_value = mock_raw_dir
        
        config = {'model_type': 'resnet18'}
        
        with pytest.raises(CommandError, match="Muy pocas imágenes raw"):
            command._validate_config(config)
    
    @patch('ml.data.dataset_loader.CacaoDatasetLoader')
    @patch('training.management.commands.train_cacao_models.get_raw_images_dir')
    def test_validate_config_too_few_csv_records(self, mock_get_raw_dir, mock_loader_class, command, tmp_path):
        """Test validation when too few CSV records."""
        mock_raw_dir = tmp_path / "raw_images"
        mock_raw_dir.mkdir()
        for i in range(15):
            (mock_raw_dir / f"image{i}.bmp").touch()
        mock_get_raw_dir.return_value = mock_raw_dir
        
        mock_loader = Mock()
        mock_loader.load_dataset.return_value = Mock(__len__=Mock(return_value=5))
        mock_loader_class.return_value = mock_loader
        
        config = {'model_type': 'resnet18'}
        
        with pytest.raises(CommandError, match="Muy pocos registros en el CSV"):
            command._validate_config(config)
    
    @patch('ml.data.dataset_loader.CacaoDatasetLoader')
    @patch('training.management.commands.train_cacao_models.get_raw_images_dir')
    def test_validate_config_too_few_valid_records(self, mock_get_raw_dir, mock_loader_class, command, tmp_path):
        """Test validation when too few valid records."""
        mock_raw_dir = tmp_path / "raw_images"
        mock_raw_dir.mkdir()
        for i in range(15):
            (mock_raw_dir / f"image{i}.bmp").touch()
        mock_get_raw_dir.return_value = mock_raw_dir
        
        mock_loader = Mock()
        mock_loader.load_dataset.return_value = Mock(__len__=Mock(return_value=20))
        mock_loader.get_valid_records.return_value = [{'id': i} for i in range(5)]
        mock_loader_class.return_value = mock_loader
        
        config = {'model_type': 'resnet18'}
        
        with pytest.raises(CommandError, match="Muy pocos registros válidos"):
            command._validate_config(config)
    
    @patch('ml.data.dataset_loader.CacaoDatasetLoader')
    @patch('training.management.commands.train_cacao_models.get_raw_images_dir')
    def test_validate_config_convnext_requires_timm(self, mock_get_raw_dir, mock_loader_class, command, tmp_path):
        """Test validation when ConvNeXt requires timm."""
        mock_raw_dir = tmp_path / "raw_images"
        mock_raw_dir.mkdir()
        for i in range(15):
            (mock_raw_dir / f"image{i}.bmp").touch()
        mock_get_raw_dir.return_value = mock_raw_dir
        
        mock_loader = Mock()
        mock_loader.load_dataset.return_value = Mock(__len__=Mock(return_value=20))
        mock_loader.get_valid_records.return_value = [{'id': i} for i in range(15)]
        mock_loader_class.return_value = mock_loader
        
        config = {'model_type': 'convnext_tiny', 'hybrid': False}
        
        # Mock the import to raise ImportError
        import sys
        original_import = __import__
        def mock_import(name, *args, **kwargs):
            if name == 'timm':
                raise ImportError("No module named 'timm'")
            return original_import(name, *args, **kwargs)
        
        with patch('builtins.__import__', side_effect=mock_import):
            with pytest.raises(CommandError, match="timm es requerido"):
                command._validate_config(config)
    
    @patch('ml.data.dataset_loader.CacaoDatasetLoader')
    @patch('training.management.commands.train_cacao_models.get_raw_images_dir')
    def test_validate_config_invalid_epochs(self, mock_get_raw_dir, mock_loader_class, command, tmp_path):
        """Test validation with invalid epochs."""
        # Mock raw images directory - need at least 10 files
        mock_raw_dir = tmp_path / "raw"
        mock_raw_dir.mkdir()
        for i in range(15):
            (mock_raw_dir / f"test{i}.bmp").touch()
        mock_get_raw_dir.return_value = mock_raw_dir
        
        # Mock dataset loader
        mock_loader = Mock()
        mock_df = Mock()
        mock_df.__len__ = Mock(return_value=20)
        mock_loader.load_dataset.return_value = mock_df
        mock_loader.get_valid_records.return_value = [{}] * 20
        mock_loader_class.return_value = mock_loader
        
        config = {'epochs': 0, 'model_type': 'resnet18', 'hybrid': False}
        
        with pytest.raises(CommandError, match="Número de épocas debe ser >= 1"):
            command._validate_config(config)
    
    @patch('ml.data.dataset_loader.CacaoDatasetLoader')
    @patch('training.management.commands.train_cacao_models.get_raw_images_dir')
    def test_validate_config_invalid_batch_size(self, mock_get_raw_dir, mock_loader_class, command, tmp_path):
        """Test validation with invalid batch size."""
        # Mock raw images directory - need at least 10 files
        mock_raw_dir = tmp_path / "raw"
        mock_raw_dir.mkdir()
        for i in range(15):
            (mock_raw_dir / f"test{i}.bmp").touch()
        mock_get_raw_dir.return_value = mock_raw_dir
        
        # Mock dataset loader
        mock_loader = Mock()
        mock_df = Mock()
        mock_df.__len__ = Mock(return_value=20)
        mock_loader.load_dataset.return_value = mock_df
        mock_loader.get_valid_records.return_value = [{}] * 20
        mock_loader_class.return_value = mock_loader
        
        config = {'batch_size': 0, 'model_type': 'resnet18', 'hybrid': False, 'epochs': 10}
        
        with pytest.raises(CommandError, match="Tamaño de batch debe ser >= 1"):
            command._validate_config(config)
    
    @patch('ml.data.dataset_loader.CacaoDatasetLoader')
    @patch('training.management.commands.train_cacao_models.get_raw_images_dir')
    def test_validate_config_invalid_learning_rate(self, mock_get_raw_dir, mock_loader_class, command, tmp_path):
        """Test validation with invalid learning rate."""
        # Mock raw images directory - need at least 10 files
        mock_raw_dir = tmp_path / "raw"
        mock_raw_dir.mkdir()
        for i in range(15):
            (mock_raw_dir / f"test{i}.bmp").touch()
        mock_get_raw_dir.return_value = mock_raw_dir
        
        # Mock dataset loader
        mock_loader = Mock()
        mock_df = Mock()
        mock_df.__len__ = Mock(return_value=20)
        mock_loader.load_dataset.return_value = mock_df
        mock_loader.get_valid_records.return_value = [{}] * 20
        mock_loader_class.return_value = mock_loader
        
        config = {'learning_rate': 0, 'model_type': 'resnet18', 'hybrid': False, 'epochs': 10, 'batch_size': 32}
        
        with pytest.raises(CommandError, match="Learning rate debe ser > 0"):
            command._validate_config(config)
    
    def test_create_config_basic(self, command, mock_options):
        """Test creating basic configuration."""
        config = command._create_config(mock_options)
        
        assert config['model_type'] == 'resnet18'
        assert config['epochs'] == 50
        assert config['batch_size'] == 32
        assert config['learning_rate'] == 1e-4
        assert config['multi_head'] is False
    
    def test_create_config_hybrid(self, command, mock_options):
        """Test creating hybrid configuration."""
        mock_options['hybrid'] = True
        config = command._create_config(mock_options)
        
        assert config['hybrid'] is True
        assert config['model_type'] == 'hybrid'
        assert config['multi_head'] is True
    
    def test_create_config_hybrid_v2(self, command, mock_options):
        """Test creating hybrid v2 configuration."""
        mock_options['hybrid_v2'] = True
        config = command._create_config(mock_options)
        
        assert config['hybrid_v2'] is True
        assert config['model_type'] == 'hybrid'
        assert config['multi_head'] is True
    
    def test_create_config_optimized_hybrid(self, command, mock_options):
        """Test creating optimized hybrid configuration."""
        mock_options['hybrid'] = True
        mock_options['use_pixel_features'] = True
        config = command._create_config(mock_options)
        
        assert config['hybrid'] is True
        assert config['use_pixel_features'] is True
        # Optimized values should be applied
        assert config['epochs'] == 100  # Optimized from 50
        assert config['learning_rate'] == 5e-5  # Optimized from 1e-4
        assert config['early_stopping_patience'] == 25  # Optimized from 15
        assert config['dropout_rate'] == 0.3  # Optimized from 0.25
    
    def test_create_config_test_mode(self, command, mock_options):
        """Test creating configuration with test mode."""
        mock_options['test_mode'] = True
        config = command._create_config(mock_options)
        
        assert config['epochs'] == 5  # Reduced from 50
        assert config['batch_size'] == 16  # Reduced from 32
        assert config['early_stopping_patience'] == 3  # Reduced from 15
    
    @patch('platform.system')
    def test_create_config_windows_num_workers(self, mock_system, command, mock_options):
        """Test that num_workers is forced to 0 on Windows."""
        mock_system.return_value = 'Windows'
        mock_options['num_workers'] = 4
        
        config = command._create_config(mock_options)
        
        assert config['num_workers'] == 0
    
    def test_get_warmup_epochs_default(self, command, mock_options):
        """Test getting default warmup epochs."""
        warmup = command._get_warmup_epochs(mock_options, is_optimized_hybrid=False)
        
        assert warmup == 5
    
    def test_get_warmup_epochs_optimized_hybrid(self, command, mock_options):
        """Test getting warmup epochs for optimized hybrid."""
        warmup = command._get_warmup_epochs(mock_options, is_optimized_hybrid=True)
        
        assert warmup == 10
    
    def test_get_warmup_epochs_explicit(self, command, mock_options):
        """Test getting explicit warmup epochs."""
        mock_options['warmup_epochs'] = 15
        warmup = command._get_warmup_epochs(mock_options, is_optimized_hybrid=False)
        
        assert warmup == 15
    
    @patch('ml.utils.paths.get_regressors_artifacts_dir')
    def test_check_models_exist_all_exist(self, mock_get_artifacts_dir, command, tmp_path):
        """Test checking models when all exist."""
        artifacts_dir = tmp_path / "artifacts"
        artifacts_dir.mkdir()
        
        for target in ['alto', 'ancho', 'grosor', 'peso']:
            (artifacts_dir / f"{target}.pt").write_bytes(b"model data")
            (artifacts_dir / f"{target}_scaler.pkl").write_bytes(b"scaler data")
        
        mock_get_artifacts_dir.return_value = artifacts_dir
        
        assert command._check_models_exist() is True
    
    @patch('ml.utils.paths.get_regressors_artifacts_dir')
    def test_check_models_exist_missing_model(self, mock_get_artifacts_dir, command, tmp_path):
        """Test checking models when a model is missing."""
        artifacts_dir = tmp_path / "artifacts"
        artifacts_dir.mkdir()
        
        for target in ['alto', 'ancho', 'grosor']:
            (artifacts_dir / f"{target}.pt").write_bytes(b"model data")
            (artifacts_dir / f"{target}_scaler.pkl").write_bytes(b"scaler data")
        
        mock_get_artifacts_dir.return_value = artifacts_dir
        
        assert command._check_models_exist() is False
    
    @patch('ml.utils.paths.get_regressors_artifacts_dir')
    def test_check_models_exist_empty_file(self, mock_get_artifacts_dir, command, tmp_path):
        """Test checking models when a file is empty."""
        artifacts_dir = tmp_path / "artifacts"
        artifacts_dir.mkdir()
        
        for target in ['alto', 'ancho', 'grosor', 'peso']:
            (artifacts_dir / f"{target}.pt").write_bytes(b"model data")
            (artifacts_dir / f"{target}_scaler.pkl").write_bytes(b"scaler data")
        
        # Make one file empty
        (artifacts_dir / "alto.pt").write_bytes(b"")
        
        mock_get_artifacts_dir.return_value = artifacts_dir
        
        assert command._check_models_exist() is False
    
    @patch('ml.utils.paths.get_regressors_artifacts_dir')
    def test_check_models_exist_exception(self, mock_get_artifacts_dir, command):
        """Test checking models when an exception occurs."""
        mock_get_artifacts_dir.side_effect = Exception("Error")
        
        assert command._check_models_exist() is False
    
    @patch('django.core.cache.cache')
    def test_check_redis_available_success(self, mock_cache, command):
        """Test checking Redis when available."""
        mock_cache.set.return_value = True
        mock_cache.get.return_value = 'test_value'
        
        assert command._check_redis_available() is True
    
    @patch('django.core.cache.cache')
    @patch('redis.Redis')
    def test_check_redis_available_cache_fails_redis_works(self, mock_redis_class, mock_cache, command):
        """Test checking Redis when cache fails but Redis works."""
        mock_cache.set.side_effect = Exception("Cache error")
        mock_redis = Mock()
        mock_redis.ping.return_value = True
        mock_redis_class.return_value = mock_redis
        
        assert command._check_redis_available() is True
    
    @patch('django.core.cache.cache')
    @patch('redis.Redis')
    def test_check_redis_available_both_fail(self, mock_redis_class, mock_cache, command):
        """Test checking Redis when both cache and Redis fail."""
        mock_cache.set.side_effect = Exception("Cache error")
        mock_redis_class.side_effect = Exception("Redis error")
        
        assert command._check_redis_available() is False

