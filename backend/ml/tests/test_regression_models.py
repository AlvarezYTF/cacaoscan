"""
Tests for regression models.
"""
import pytest
import torch
import torch.nn as nn
from unittest.mock import patch, Mock
from ml.regression.models import (
    ResNet18Regression,
    init_linear_and_batchnorm_weights,
    create_model,
    TARGETS
)


class TestResNet18Regression:
    """Tests for ResNet18Regression class."""
    
    def test_initialization_pretrained(self):
        """Test model initialization with pretrained weights."""
        model = ResNet18Regression(num_outputs=4, pretrained=True)
        
        assert model.num_outputs == 4
        assert hasattr(model, 'backbone')
    
    def test_initialization_not_pretrained(self):
        """Test model initialization without pretrained weights."""
        model = ResNet18Regression(num_outputs=4, pretrained=False)
        
        assert model.num_outputs == 4
    
    def test_forward_pass(self):
        """Test forward pass."""
        model = ResNet18Regression(num_outputs=4, pretrained=False)
        model.eval()
        
        x = torch.randn(2, 3, 224, 224)
        
        with torch.no_grad():
            output = model(x)
        
        assert output.shape == (2, 4)
    
    def test_get_features(self):
        """Test getting features."""
        model = ResNet18Regression(num_outputs=4, pretrained=False)
        model.eval()
        
        x = torch.randn(2, 3, 224, 224)
        
        with torch.no_grad():
            features = model.get_features(x)
        
        assert features.shape[0] == 2
        assert features.ndim == 2
    
    def test_different_num_outputs(self):
        """Test model with different number of outputs."""
        model = ResNet18Regression(num_outputs=1, pretrained=False)
        
        x = torch.randn(1, 3, 224, 224)
        
        with torch.no_grad():
            output = model(x)
        
        assert output.shape == (1, 1)


class TestInitLinearAndBatchNormWeights:
    """Tests for init_linear_and_batchnorm_weights function."""
    
    def test_init_weights_linear(self):
        """Test initializing Linear layer weights."""
        linear = nn.Linear(10, 5)
        
        init_linear_and_batchnorm_weights(linear)
        
        assert linear.weight is not None
        assert linear.bias is not None
    
    def test_init_weights_batchnorm(self):
        """Test initializing BatchNorm1d layer weights."""
        batchnorm = nn.BatchNorm1d(10)
        
        init_linear_and_batchnorm_weights(batchnorm)
        
        assert batchnorm.weight is not None
        assert batchnorm.bias is not None
    
    def test_init_weights_sequential(self):
        """Test initializing weights in Sequential module."""
        module = nn.Sequential(
            nn.Linear(10, 5),
            nn.BatchNorm1d(5),
            nn.Linear(5, 1)
        )
        
        init_linear_and_batchnorm_weights(module)
        
        assert all(isinstance(m, (nn.Linear, nn.BatchNorm1d)) for m in module)


class TestCreateModel:
    """Tests for create_model function."""
    
    def test_create_model_resnet18(self):
        """Test creating ResNet18 model."""
        model = create_model('resnet18', num_outputs=4, pretrained=False)
        
        assert isinstance(model, ResNet18Regression)
        assert model.num_outputs == 4
    
    def test_create_model_resnet34(self):
        """Test creating ResNet34 model."""
        model = create_model('resnet34', num_outputs=4, pretrained=False)
        
        assert model.num_outputs == 4
    
    @patch('ml.regression.models.TIMM_AVAILABLE', True)
    @patch('ml.regression.models.timm')
    def test_create_model_convnext(self, mock_timm):
        """Test creating ConvNeXt model."""
        mock_backbone = Mock()
        mock_timm.create_model.return_value = mock_backbone
        
        model = create_model('convnext_tiny', num_outputs=4, pretrained=False)
        
        assert model is not None
    
    def test_create_model_invalid_type(self):
        """Test creating model with invalid type."""
        with pytest.raises(ValueError, match="no soportado"):
            create_model('invalid_model', num_outputs=4)
    
    def test_create_model_different_outputs(self):
        """Test creating model with different number of outputs."""
        model = create_model('resnet18', num_outputs=1, pretrained=False)
        
        x = torch.randn(1, 3, 224, 224)
        
        with torch.no_grad():
            output = model(x)
        
        assert output.shape == (1, 1)

