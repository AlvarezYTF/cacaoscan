"""
Tests for hybrid regression model.
"""
import pytest
import torch
import torch.nn as nn
from unittest.mock import patch, MagicMock
from ml.regression.hybrid_model import HybridRegressor, create_hybrid_model


@pytest.mark.skipif(
    not hasattr(nn.Module, '__module__'),
    reason="PyTorch not available or incompatible"
)
class TestHybridRegressor:
    """Tests for HybridRegressor class."""
    
    @patch('ml.regression.hybrid_model.TIMM_AVAILABLE', True)
    @patch('ml.regression.hybrid_model.timm')
    def test_initialization(self, mock_timm):
        """Test model initialization."""
        # Mock timm model creation
        mock_backbone = MagicMock()
        mock_backbone.num_features = 768
        mock_timm.create_model.return_value = mock_backbone
        
        model = HybridRegressor(
            backbone_name="convnext_tiny",
            pixel_dim=10,
            pretrained=True,
            dropout_rate=0.1
        )
        
        assert model is not None
        assert hasattr(model, 'backbone')
        assert hasattr(model, 'img_projection')
        assert hasattr(model, 'pix_projection')
        assert hasattr(model, 'fusion_layer')
        assert hasattr(model, 'mlp')
    
    @patch('ml.regression.hybrid_model.TIMM_AVAILABLE', False)
    def test_initialization_no_timm(self):
        """Test initialization fails when timm is not available."""
        with pytest.raises(ImportError, match="timm es requerido"):
            HybridRegressor()
    
    @patch('ml.regression.hybrid_model.TIMM_AVAILABLE', True)
    @patch('ml.regression.hybrid_model.timm')
    def test_forward_with_pixel_features(self, mock_timm):
        """Test forward pass with pixel features."""
        # Mock timm model creation
        mock_backbone = MagicMock()
        mock_backbone.num_features = 768
        mock_backbone.return_value = torch.randn(2, 768)
        mock_timm.create_model.return_value = mock_backbone
        
        model = HybridRegressor(pixel_dim=10, pretrained=False)
        model.eval()
        
        images = torch.randn(2, 3, 224, 224)
        pixel_features = torch.randn(2, 10)
        
        with torch.no_grad():
            output = model(images, pixel_features)
        
        assert output is not None
        assert isinstance(output, dict)
        assert 'alto' in output
        assert 'ancho' in output
        assert 'grosor' in output
        assert 'peso' in output
    
    @patch('ml.regression.hybrid_model.TIMM_AVAILABLE', True)
    @patch('ml.regression.hybrid_model.timm')
    def test_forward_without_pixel_features(self, mock_timm):
        """Test forward pass without pixel features (uses zeros)."""
        # Mock timm model creation
        mock_backbone = MagicMock()
        mock_backbone.num_features = 768
        mock_backbone.return_value = torch.randn(2, 768)
        mock_timm.create_model.return_value = mock_backbone
        
        model = HybridRegressor(pixel_dim=10, pretrained=False)
        model.eval()
        
        images = torch.randn(2, 3, 224, 224)
        
        with torch.no_grad():
            output = model(images)
        
        assert output is not None
        assert isinstance(output, dict)


class TestCreateHybridModel:
    """Tests for create_hybrid_model function."""
    
    @patch('ml.regression.hybrid_model.TIMM_AVAILABLE', True)
    @patch('ml.regression.hybrid_model.timm')
    def test_create_hybrid_model_default(self, mock_timm):
        """Test creating hybrid model with default parameters."""
        # Mock timm model creation
        mock_backbone = MagicMock()
        mock_backbone.num_features = 768
        mock_timm.create_model.return_value = mock_backbone
        
        model = create_hybrid_model()
        
        assert model is not None
        assert isinstance(model, HybridRegressor)
    
    @patch('ml.regression.hybrid_model.TIMM_AVAILABLE', True)
    @patch('ml.regression.hybrid_model.timm')
    def test_create_hybrid_model_custom(self, mock_timm):
        """Test creating hybrid model with custom parameters."""
        # Mock timm model creation
        mock_backbone = MagicMock()
        mock_backbone.num_features = 768
        mock_timm.create_model.return_value = mock_backbone
        
        model = create_hybrid_model(
            backbone_name="convnext_tiny",
            pixel_dim=10,
            pretrained=False,
            dropout_rate=0.2
        )
        
        assert model is not None


