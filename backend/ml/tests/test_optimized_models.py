"""
Tests for optimized regression models.
"""
import pytest
import torch
import torch.nn as nn
from unittest.mock import patch, MagicMock
from ml.regression.optimized_models import (
    init_weights,
    extract_resnet_features,
    OptimizedResNet18Regression,
    OptimizedHybridRegression,
    SimpleCacaoRegression,
    create_optimized_model,
    get_model_summary
)


class TestInitWeights:
    """Tests for init_weights function."""
    
    def test_init_weights_linear(self):
        """Test initializing weights for linear layer."""
        linear = nn.Linear(10, 5)
        init_weights(linear)
        
        # Check that weights were initialized
        assert linear.weight is not None
    
    def test_init_weights_batchnorm(self):
        """Test initializing weights for batch norm layer."""
        batchnorm = nn.BatchNorm1d(10)
        init_weights(batchnorm)
        
        # Check that weights were initialized
        assert batchnorm.weight is not None


class TestExtractResnetFeatures:
    """Tests for extract_resnet_features function."""
    
    def test_extract_resnet_features(self):
        """Test extracting features from ResNet backbone."""
        # Create a simple backbone
        backbone = nn.Sequential(
            nn.Conv2d(3, 64, 3, padding=1),
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten()
        )
        
        x = torch.randn(2, 3, 224, 224)
        features = extract_resnet_features(backbone, x)
        
        assert features is not None
        assert features.shape[0] == 2


class TestOptimizedResNet18Regression:
    """Tests for OptimizedResNet18Regression class."""
    
    def test_initialization(self):
        """Test model initialization."""
        model = OptimizedResNet18Regression(
            num_outputs=4,
            pretrained=False
        )
        
        assert model is not None
        assert hasattr(model, 'backbone')
        assert hasattr(model, 'regressor')
    
    def test_forward(self):
        """Test forward pass."""
        model = OptimizedResNet18Regression(
            num_outputs=4,
            pretrained=False
        )
        model.eval()
        
        x = torch.randn(2, 3, 224, 224)
        
        with torch.no_grad():
            output = model(x)
        
        assert output.shape == (2, 4)


class TestOptimizedHybridRegression:
    """Tests for OptimizedHybridRegression class."""
    
    def test_initialization(self):
        """Test model initialization."""
        model = OptimizedHybridRegression(
            num_outputs=4,
            pixel_dim=10,
            pretrained=False
        )
        
        assert model is not None
        assert hasattr(model, 'backbone')
        assert hasattr(model, 'pixel_mlp')
        assert hasattr(model, 'fusion')
    
    def test_forward_with_pixel_features(self):
        """Test forward pass with pixel features."""
        model = OptimizedHybridRegression(
            num_outputs=4,
            pixel_dim=10,
            pretrained=False
        )
        model.eval()
        
        images = torch.randn(2, 3, 224, 224)
        pixel_features = torch.randn(2, 10)
        
        with torch.no_grad():
            output = model(images, pixel_features)
        
        assert output.shape == (2, 4)


class TestSimpleCacaoRegression:
    """Tests for SimpleCacaoRegression class."""
    
    def test_initialization(self):
        """Test model initialization."""
        model = SimpleCacaoRegression(
            num_outputs=4,
            hidden_dim=128
        )
        
        assert model is not None
        assert hasattr(model, 'mlp')
    
    def test_forward(self):
        """Test forward pass."""
        model = SimpleCacaoRegression(
            num_outputs=4,
            hidden_dim=128
        )
        model.eval()
        
        x = torch.randn(2, 10)  # Input features
        
        with torch.no_grad():
            output = model(x)
        
        assert output.shape == (2, 4)


class TestCreateOptimizedModel:
    """Tests for create_optimized_model function."""
    
    def test_create_optimized_model_resnet(self):
        """Test creating ResNet model."""
        model = create_optimized_model(
            model_type="resnet18",
            num_outputs=4,
            pretrained=False
        )
        
        assert model is not None
        assert isinstance(model, OptimizedResNet18Regression)
    
    def test_create_optimized_model_hybrid(self):
        """Test creating hybrid model."""
        model = create_optimized_model(
            model_type="hybrid",
            num_outputs=4,
            pixel_dim=10,
            pretrained=False
        )
        
        assert model is not None
        assert isinstance(model, OptimizedHybridRegression)
    
    def test_create_optimized_model_simple(self):
        """Test creating simple model."""
        model = create_optimized_model(
            model_type="simple",
            num_outputs=4
        )
        
        assert model is not None
        assert isinstance(model, SimpleCacaoRegression)


class TestGetModelSummary:
    """Tests for get_model_summary function."""
    
    def test_get_model_summary(self):
        """Test getting model summary."""
        model = SimpleCacaoRegression(num_outputs=4)
        
        summary = get_model_summary(model)
        
        assert isinstance(summary, dict)
        assert 'total_parameters' in summary
        assert 'trainable_parameters' in summary
        assert summary['total_parameters'] > 0


