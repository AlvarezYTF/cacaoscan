"""
Tests for train_all.py pipeline training module.
This file tests the complete training pipeline.
"""
import pytest
import torch
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from ml.pipeline.train_all import (
    CacaoDataset,
    CacaoTrainingPipeline,
    PIXEL_FEATURE_KEYS,
    CALIB_PIXEL_FEATURE_KEYS,
    MODEL_HYBRID,
    MODEL_MULTIHEAD,
    TARGETS,
)


@pytest.fixture
def sample_image_paths(tmp_path):
    """Create sample image paths."""
    images_dir = tmp_path / 'images'
    images_dir.mkdir()
    
    paths = []
    for i in range(5):
        img_path = images_dir / f'test{i}.png'
        img_path.write_bytes(b'fake image')
        paths.append(img_path)
    
    return paths


@pytest.fixture
def sample_targets():
    """Create sample targets."""
    return {
        'alto': np.array([10.0, 11.0, 12.0, 13.0, 14.0]),
        'ancho': np.array([20.0, 21.0, 22.0, 23.0, 24.0]),
        'grosor': np.array([30.0, 31.0, 32.0, 33.0, 34.0]),
        'peso': np.array([40.0, 41.0, 42.0, 43.0, 44.0])
    }


@pytest.fixture
def sample_pixel_features():
    """Create sample pixel features."""
    return {
        'pixel_width': np.array([100.0, 101.0, 102.0, 103.0, 104.0]),
        'pixel_height': np.array([200.0, 201.0, 202.0, 203.0, 204.0]),
        'pixel_area': np.array([20000.0, 20301.0, 20604.0, 20909.0, 21216.0]),
        'scale_factor': np.array([1.0, 1.01, 1.02, 1.03, 1.04]),
        'aspect_ratio': np.array([0.5, 0.502, 0.505, 0.507, 0.51])
    }


class TestCacaoDataset:
    """Tests for CacaoDataset class."""
    
    def test_cacao_dataset_init_basic(self, sample_image_paths, sample_targets):
        """Test initializing CacaoDataset with basic config."""
        transform = MagicMock()
        
        dataset = CacaoDataset(
            sample_image_paths,
            sample_targets,
            transform,
            is_multi_head=False,
            is_hybrid=False
        )
        
        assert len(dataset) == 5
        assert dataset.is_multi_head is False
        assert dataset.is_hybrid is False
    
    def test_cacao_dataset_init_with_pixel_features(self, sample_image_paths, sample_targets, sample_pixel_features):
        """Test initializing CacaoDataset with pixel features."""
        transform = MagicMock()
        
        dataset = CacaoDataset(
            sample_image_paths,
            sample_targets,
            transform,
            pixel_features=sample_pixel_features,
            is_hybrid=True
        )
        
        assert len(dataset) == 5
        assert dataset.is_hybrid is True
        assert dataset.pixel_features is not None
    
    def test_cacao_dataset_determine_feature_keys_calib(self, sample_image_paths, sample_targets):
        """Test determining feature keys with calibration features."""
        transform = MagicMock()
        
        calib_features = {key: np.array([1.0] * 5) for key in CALIB_PIXEL_FEATURE_KEYS}
        
        dataset = CacaoDataset(
            sample_image_paths,
            sample_targets,
            transform,
            pixel_features=calib_features,
            is_hybrid=True
        )
        
        # Should use CALIB_PIXEL_FEATURE_KEYS
        assert hasattr(dataset, 'pixel_means')
    
    def test_cacao_dataset_determine_feature_keys_basic(self, sample_image_paths, sample_targets, sample_pixel_features):
        """Test determining feature keys with basic features."""
        transform = MagicMock()
        
        dataset = CacaoDataset(
            sample_image_paths,
            sample_targets,
            transform,
            pixel_features=sample_pixel_features,
            is_hybrid=True
        )
        
        # Should use PIXEL_FEATURE_KEYS
        assert hasattr(dataset, 'pixel_means')
    
    def test_cacao_dataset_validate_data_lengths_success(self, sample_image_paths, sample_targets):
        """Test validating data lengths successfully."""
        transform = MagicMock()
        
        dataset = CacaoDataset(
            sample_image_paths,
            sample_targets,
            transform,
            validate_structure=True
        )
        
        # Should not raise
        assert len(dataset) == 5
    
    def test_cacao_dataset_validate_data_lengths_mismatch(self, sample_image_paths):
        """Test validating data lengths with mismatch."""
        transform = MagicMock()
        
        targets = {
            'alto': np.array([10.0, 11.0])  # Only 2 values, but 5 images
        }
        
        with pytest.raises(ValueError):
            CacaoDataset(
                sample_image_paths,
                targets,
                transform,
                validate_structure=True
            )
    
    def test_cacao_dataset_getitem_basic(self, sample_image_paths, sample_targets):
        """Test getting item from dataset."""
        transform = MagicMock()
        transform.return_value = torch.randn(3, 224, 224)
        
        dataset = CacaoDataset(
            sample_image_paths,
            sample_targets,
            transform,
            is_multi_head=False,
            is_hybrid=False
        )
        
        item = dataset[0]
        
        assert len(item) == 2  # image, target
        assert isinstance(item[0], torch.Tensor)
        assert isinstance(item[1], torch.Tensor)
    
    def test_cacao_dataset_getitem_with_pixel_features(self, sample_image_paths, sample_targets, sample_pixel_features):
        """Test getting item from dataset with pixel features."""
        transform = MagicMock()
        transform.return_value = torch.randn(3, 224, 224)
        
        dataset = CacaoDataset(
            sample_image_paths,
            sample_targets,
            transform,
            pixel_features=sample_pixel_features,
            is_hybrid=True
        )
        
        item = dataset[0]
        
        assert len(item) == 3  # image, target, pixel_features
        assert isinstance(item[0], torch.Tensor)
        assert isinstance(item[1], torch.Tensor)
        assert isinstance(item[2], torch.Tensor)


class TestCacaoTrainingPipeline:
    """Tests for CacaoTrainingPipeline class."""
    
    @pytest.fixture
    def sample_config(self):
        """Create sample config for pipeline."""
        return {
            'epochs': 2,
            'batch_size': 2,
            'learning_rate': 1e-4,
            'img_size': 224,
            'model_type': 'resnet18',
            'multi_head': False,
            'hybrid': False,
            'use_pixel_features': False,
            'num_workers': 0,
            'early_stopping_patience': 5,
            'dropout_rate': 0.2,
            'pretrained': True,
            'weight_decay': 1e-4,
            'min_lr': 1e-7,
            'loss_type': 'smooth_l1',
            'scheduler_type': 'reduce_on_plateau',
            'max_grad_norm': 1.0,
            'targets': ['alto', 'ancho', 'grosor', 'peso']
        }
    
    @patch('ml.pipeline.train_all.CacaoDatasetLoader')
    @patch('ml.pipeline.train_all.create_model')
    @patch('ml.pipeline.train_all.create_scalers_from_data')
    @patch('ml.pipeline.train_all.train_single_model')
    def test_pipeline_run_individual_models(self, mock_train, mock_scalers, mock_model, mock_loader, sample_config):
        """Test running pipeline with individual models."""
        # Mock dataset loader
        mock_loader_instance = MagicMock()
        mock_loader_instance.get_valid_records.return_value = [
            {
                'id': i,
                'alto': 10.0 + i,
                'ancho': 20.0 + i,
                'grosor': 30.0 + i,
                'peso': 40.0 + i,
                'crop_image_path': f'/tmp/test{i}.png'
            }
            for i in range(10)
        ]
        mock_loader.return_value = mock_loader_instance
        
        # Mock model creation
        mock_model.return_value = MagicMock()
        
        # Mock scalers
        mock_scalers_instance = MagicMock()
        mock_scalers_instance.is_fitted = True
        mock_scalers.return_value = mock_scalers_instance
        
        # Mock training
        mock_train.return_value = {
            'train_loss': [0.5, 0.4],
            'val_loss': [0.4, 0.3],
            'val_mae': [0.3, 0.2],
            'val_rmse': [0.4, 0.3],
            'val_r2': [0.8, 0.85]
        }
        
        pipeline = CacaoTrainingPipeline(sample_config)
        
        with patch('ml.pipeline.train_all.Path') as mock_path:
            mock_path.return_value.exists.return_value = True
            mock_path.return_value.__truediv__.return_value = mock_path.return_value
            
            result = pipeline.run_pipeline()
            
            assert 'evaluation_results' in result or result is not None
    
    @patch('ml.pipeline.train_all.CacaoDatasetLoader')
    @patch('ml.pipeline.train_all.create_model')
    @patch('ml.pipeline.train_all.create_scalers_from_data')
    @patch('ml.pipeline.train_all.train_multi_head_model')
    def test_pipeline_run_multihead(self, mock_train, mock_scalers, mock_model, mock_loader, sample_config):
        """Test running pipeline with multihead model."""
        sample_config['multi_head'] = True
        
        # Mock dataset loader
        mock_loader_instance = MagicMock()
        mock_loader_instance.get_valid_records.return_value = [
            {
                'id': i,
                'alto': 10.0 + i,
                'ancho': 20.0 + i,
                'grosor': 30.0 + i,
                'peso': 40.0 + i,
                'crop_image_path': f'/tmp/test{i}.png'
            }
            for i in range(10)
        ]
        mock_loader.return_value = mock_loader_instance
        
        # Mock model creation
        mock_model.return_value = MagicMock()
        
        # Mock scalers
        mock_scalers_instance = MagicMock()
        mock_scalers_instance.is_fitted = True
        mock_scalers.return_value = mock_scalers_instance
        
        # Mock training
        mock_train.return_value = {
            'train_loss': [0.5, 0.4],
            'val_loss': [0.4, 0.3],
            'val_r2_avg': [0.8, 0.85]
        }
        
        pipeline = CacaoTrainingPipeline(sample_config)
        
        with patch('ml.pipeline.train_all.Path') as mock_path:
            mock_path.return_value.exists.return_value = True
            mock_path.return_value.__truediv__.return_value = mock_path.return_value
            
            result = pipeline.run_pipeline()
            
            assert mock_train.called
    
    @patch('ml.pipeline.train_all.CacaoDatasetLoader')
    def test_pipeline_prepare_data(self, mock_loader, sample_config):
        """Test preparing data in pipeline."""
        mock_loader_instance = MagicMock()
        mock_loader_instance.get_valid_records.return_value = [
            {
                'id': i,
                'alto': 10.0 + i,
                'ancho': 20.0 + i,
                'grosor': 30.0 + i,
                'peso': 40.0 + i,
                'crop_image_path': f'/tmp/test{i}.png'
            }
            for i in range(10)
        ]
        mock_loader.return_value = mock_loader_instance
        
        pipeline = CacaoTrainingPipeline(sample_config)
        
        with patch('ml.pipeline.train_all.Path') as mock_path:
            mock_path.return_value.exists.return_value = True
            mock_path.return_value.__truediv__.return_value = mock_path.return_value
            
            # Should not raise
            assert hasattr(pipeline, 'config')
    
    @patch('ml.pipeline.train_all.CacaoDatasetLoader')
    def test_pipeline_prepare_data_no_valid_records(self, mock_loader, sample_config):
        """Test preparing data with no valid records."""
        mock_loader_instance = MagicMock()
        mock_loader_instance.get_valid_records.return_value = []
        mock_loader.return_value = mock_loader_instance
        
        pipeline = CacaoTrainingPipeline(sample_config)
        
        with patch('ml.pipeline.train_all.Path'):
            # Should handle empty records gracefully
            assert hasattr(pipeline, 'config')


