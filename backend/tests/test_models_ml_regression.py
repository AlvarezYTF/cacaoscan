"""
Unit tests for ml.regression models (PyTorch models).
Tests cover model initialization, forward pass, and helper functions.
Note: These are PyTorch models, not Django models.
"""
import pytest
import torch
import torch.nn as nn

# Skip tests if torch is not available
pytest.importorskip("torch")

from ml.regression.models import (
    ResNet18Regression,
    ConvNeXtTinyRegression,
    MultiHeadRegression,
    HybridCacaoRegression,
    create_model,
    get_model_info,
    count_parameters,
    verify_convnext_weights,
    create_convnext_backbone,
    init_linear_and_batchnorm_weights
)


class TestResNet18Regression:
    """Tests for ResNet18Regression model."""
    
    def test_resnet18_initialization_pretrained(self):
        """Test ResNet18Regression initialization with pretrained weights."""
        model = ResNet18Regression(
            num_outputs=1,
            pretrained=True,
            dropout_rate=0.3
        )
        
        assert model.num_outputs == 1
        assert isinstance(model.backbone, nn.Module)
        assert hasattr(model.backbone, 'fc')
    
    def test_resnet18_initialization_no_pretrained(self):
        """Test ResNet18Regression initialization without pretrained weights."""
        model = ResNet18Regression(
            num_outputs=1,
            pretrained=False,
            dropout_rate=0.3
        )
        
        assert model.num_outputs == 1
        assert isinstance(model.backbone, nn.Module)
    
    def test_resnet18_forward_pass(self):
        """Test ResNet18Regression forward pass."""
        model = ResNet18Regression(
            num_outputs=1,
            pretrained=False,
            dropout_rate=0.3
        )
        model.eval()
        
        # Create dummy input
        batch_size = 2
        x = torch.randn(batch_size, 3, 224, 224)
        
        output = model(x)
        
        assert output.shape == (batch_size, 1)
        assert not torch.isnan(output).any()
    
    def test_resnet18_get_features(self):
        """Test ResNet18Regression get_features method."""
        model = ResNet18Regression(
            num_outputs=1,
            pretrained=False,
            dropout_rate=0.3
        )
        model.eval()
        
        batch_size = 2
        x = torch.randn(batch_size, 3, 224, 224)
        
        features = model.get_features(x)
        
        assert features.shape[0] == batch_size
        assert features.shape[1] == 512  # ResNet18 features
        assert not torch.isnan(features).any()
    
    def test_resnet18_multiple_outputs(self):
        """Test ResNet18Regression with multiple outputs."""
        model = ResNet18Regression(
            num_outputs=4,
            pretrained=False,
            dropout_rate=0.3
        )
        model.eval()
        
        batch_size = 2
        x = torch.randn(batch_size, 3, 224, 224)
        
        output = model(x)
        
        assert output.shape == (batch_size, 4)


class TestConvNeXtTinyRegression:
    """Tests for ConvNeXtTinyRegression model."""
    
    @pytest.mark.skipif(
        not pytest.importorskip("timm", reason="timm not available"),
        reason="timm is required for ConvNeXt"
    )
    def test_convnext_initialization_pretrained(self):
        """Test ConvNeXtTinyRegression initialization with pretrained weights."""
        try:
            model = ConvNeXtTinyRegression(
                num_outputs=1,
                pretrained=True,
                dropout_rate=0.2
            )
            
            assert model.num_outputs == 1
            assert isinstance(model.backbone, nn.Module)
            assert hasattr(model, 'regression_head')
        except ImportError:
            pytest.skip("timm not available")
    
    @pytest.mark.skipif(
        not pytest.importorskip("timm", reason="timm not available"),
        reason="timm is required for ConvNeXt"
    )
    def test_convnext_initialization_no_pretrained(self):
        """Test ConvNeXtTinyRegression initialization without pretrained weights."""
        try:
            model = ConvNeXtTinyRegression(
                num_outputs=1,
                pretrained=False,
                dropout_rate=0.2
            )
            
            assert model.num_outputs == 1
            assert isinstance(model.backbone, nn.Module)
        except ImportError:
            pytest.skip("timm not available")
    
    @pytest.mark.skipif(
        not pytest.importorskip("timm", reason="timm not available"),
        reason="timm is required for ConvNeXt"
    )
    def test_convnext_forward_pass(self):
        """Test ConvNeXtTinyRegression forward pass."""
        try:
            model = ConvNeXtTinyRegression(
                num_outputs=1,
                pretrained=False,
                dropout_rate=0.2
            )
            model.eval()
            
            batch_size = 2
            x = torch.randn(batch_size, 3, 224, 224)
            
            output = model(x)
            
            assert output.shape == (batch_size, 1)
            assert not torch.isnan(output).any()
        except ImportError:
            pytest.skip("timm not available")
    
    @pytest.mark.skipif(
        not pytest.importorskip("timm", reason="timm not available"),
        reason="timm is required for ConvNeXt"
    )
    def test_convnext_get_features(self):
        """Test ConvNeXtTinyRegression get_features method."""
        try:
            model = ConvNeXtTinyRegression(
                num_outputs=1,
                pretrained=False,
                dropout_rate=0.2
            )
            model.eval()
            
            batch_size = 2
            x = torch.randn(batch_size, 3, 224, 224)
            
            features = model.get_features(x)
            
            assert features.shape[0] == batch_size
            assert not torch.isnan(features).any()
        except ImportError:
            pytest.skip("timm not available")


class TestMultiHeadRegression:
    """Tests for MultiHeadRegression model."""
    
    def test_multihead_initialization_resnet18(self):
        """Test MultiHeadRegression initialization with ResNet18 backbone."""
        model = MultiHeadRegression(
            backbone_type='resnet18',
            pretrained=False,
            dropout_rate=0.2,
            shared_features=True
        )
        
        assert model.backbone_type == 'resnet18'
        assert model.shared_features is True
        assert hasattr(model, 'heads')
        assert 'alto' in model.heads
        assert 'ancho' in model.heads
        assert 'grosor' in model.heads
        assert 'peso' in model.heads
    
    @pytest.mark.skipif(
        not pytest.importorskip("timm", reason="timm not available"),
        reason="timm is required for ConvNeXt"
    )
    def test_multihead_initialization_convnext(self):
        """Test MultiHeadRegression initialization with ConvNeXt backbone."""
        try:
            model = MultiHeadRegression(
                backbone_type='convnext_tiny',
                pretrained=False,
                dropout_rate=0.2,
                shared_features=True
            )
            
            assert model.backbone_type == 'convnext_tiny'
            assert hasattr(model, 'heads')
        except ImportError:
            pytest.skip("timm not available")
    
    def test_multihead_forward_pass_shared(self):
        """Test MultiHeadRegression forward pass with shared features."""
        model = MultiHeadRegression(
            backbone_type='resnet18',
            pretrained=False,
            dropout_rate=0.2,
            shared_features=True
        )
        model.eval()
        
        batch_size = 2
        x = torch.randn(batch_size, 3, 224, 224)
        
        output = model(x)
        
        assert isinstance(output, dict)
        assert 'alto' in output
        assert 'ancho' in output
        assert 'grosor' in output
        assert 'peso' in output
        assert output['alto'].shape == (batch_size, 1)
    
    def test_multihead_forward_pass_individual(self):
        """Test MultiHeadRegression forward pass with individual heads."""
        model = MultiHeadRegression(
            backbone_type='resnet18',
            pretrained=False,
            dropout_rate=0.2,
            shared_features=False
        )
        model.eval()
        
        batch_size = 2
        x = torch.randn(batch_size, 3, 224, 224)
        
        output = model(x)
        
        assert isinstance(output, dict)
        assert 'alto' in output
        assert output['alto'].shape == (batch_size, 1)
    
    def test_multihead_forward_single(self):
        """Test MultiHeadRegression forward_single method."""
        model = MultiHeadRegression(
            backbone_type='resnet18',
            pretrained=False,
            dropout_rate=0.2,
            shared_features=False
        )
        model.eval()
        
        batch_size = 2
        x = torch.randn(batch_size, 3, 224, 224)
        
        output = model.forward_single(x, 'alto')
        
        assert output.shape == (batch_size, 1)
    
    def test_multihead_invalid_backbone(self):
        """Test MultiHeadRegression with invalid backbone type."""
        with pytest.raises(ValueError):
            MultiHeadRegression(
                backbone_type='invalid',
                pretrained=False,
                dropout_rate=0.2
            )


class TestHybridCacaoRegression:
    """Tests for HybridCacaoRegression model."""
    
    @pytest.mark.skipif(
        not pytest.importorskip("timm", reason="timm not available"),
        reason="timm is required for HybridCacaoRegression"
    )
    def test_hybrid_initialization(self):
        """Test HybridCacaoRegression initialization."""
        try:
            model = HybridCacaoRegression(
                num_outputs=4,
                pretrained=False,
                dropout_rate=0.3,
                num_pixel_features=10,
                use_pixel_features=True
            )
            
            assert model.num_outputs == 4
            assert model.use_pixel_features is True
            assert hasattr(model, 'resnet18')
            assert hasattr(model, 'convnext')
        except ImportError:
            pytest.skip("timm not available")
    
    @pytest.mark.skipif(
        not pytest.importorskip("timm", reason="timm not available"),
        reason="timm is required for HybridCacaoRegression"
    )
    def test_hybrid_forward_pass_with_pixel_features(self):
        """Test HybridCacaoRegression forward pass with pixel features."""
        try:
            model = HybridCacaoRegression(
                num_outputs=4,
                pretrained=False,
                dropout_rate=0.3,
                num_pixel_features=10,
                use_pixel_features=True
            )
            model.eval()
            
            batch_size = 2
            image = torch.randn(batch_size, 3, 224, 224)
            pixel_features = torch.randn(batch_size, 10)
            
            output = model(image, pixel_features)
            
            assert isinstance(output, dict)
            assert 'alto' in output
            assert 'ancho' in output
            assert 'grosor' in output
            assert 'peso' in output
            assert output['alto'].shape == (batch_size, 1)
        except ImportError:
            pytest.skip("timm not available")
    
    @pytest.mark.skipif(
        not pytest.importorskip("timm", reason="timm not available"),
        reason="timm is required for HybridCacaoRegression"
    )
    def test_hybrid_forward_pass_without_pixel_features(self):
        """Test HybridCacaoRegression forward pass without pixel features."""
        try:
            model = HybridCacaoRegression(
                num_outputs=4,
                pretrained=False,
                dropout_rate=0.3,
                num_pixel_features=10,
                use_pixel_features=False
            )
            model.eval()
            
            batch_size = 2
            image = torch.randn(batch_size, 3, 224, 224)
            
            output = model(image)
            
            assert isinstance(output, dict)
            assert 'alto' in output
        except ImportError:
            pytest.skip("timm not available")
    
    @pytest.mark.skipif(
        not pytest.importorskip("timm", reason="timm not available"),
        reason="timm is required for HybridCacaoRegression"
    )
    def test_hybrid_get_features(self):
        """Test HybridCacaoRegression get_features method."""
        try:
            model = HybridCacaoRegression(
                num_outputs=4,
                pretrained=False,
                dropout_rate=0.3,
                num_pixel_features=10,
                use_pixel_features=True
            )
            model.eval()
            
            batch_size = 2
            image = torch.randn(batch_size, 3, 224, 224)
            pixel_features = torch.randn(batch_size, 10)
            
            features = model.get_features(image, pixel_features)
            
            assert features.shape[0] == batch_size
            assert not torch.isnan(features).any()
        except ImportError:
            pytest.skip("timm not available")


class TestModelFactoryFunctions:
    """Tests for model factory functions."""
    
    def test_create_model_resnet18(self):
        """Test create_model function for ResNet18."""
        model = create_model(
            model_type='resnet18',
            num_outputs=1,
            pretrained=False,
            dropout_rate=0.3
        )
        
        assert model is not None
        assert isinstance(model, nn.Module)
    
    @pytest.mark.skipif(
        not pytest.importorskip("timm", reason="timm not available"),
        reason="timm is required for ConvNeXt"
    )
    def test_create_model_convnext(self):
        """Test create_model function for ConvNeXt."""
        try:
            model = create_model(
                model_type='convnext_tiny',
                num_outputs=1,
                pretrained=False,
                dropout_rate=0.2
            )
            
            assert model is not None
            assert isinstance(model, nn.Module)
        except ImportError:
            pytest.skip("timm not available")
    
    def test_create_model_multi_head(self):
        """Test create_model function for multi-head."""
        model = create_model(
            model_type='resnet18',
            num_outputs=1,
            pretrained=False,
            dropout_rate=0.2,
            multi_head=True
        )
        
        assert model is not None
        assert isinstance(model, MultiHeadRegression)
    
    @pytest.mark.skipif(
        not pytest.importorskip("timm", reason="timm not available"),
        reason="timm is required for Hybrid"
    )
    def test_create_model_hybrid(self):
        """Test create_model function for hybrid."""
        try:
            model = create_model(
                model_type='resnet18',
                num_outputs=4,
                pretrained=False,
                dropout_rate=0.3,
                hybrid=True,
                use_pixel_features=True
            )
            
            assert model is not None
            assert isinstance(model, HybridCacaoRegression)
        except ImportError:
            pytest.skip("timm not available")
    
    def test_get_model_info(self):
        """Test get_model_info function."""
        model = ResNet18Regression(
            num_outputs=1,
            pretrained=False,
            dropout_rate=0.3
        )
        
        info = get_model_info(model)
        
        assert isinstance(info, dict)
        assert 'total_parameters' in info
        assert 'trainable_parameters' in info
        assert 'model_type' in info
        assert info['total_parameters'] > 0
        assert info['trainable_parameters'] > 0
    
    def test_count_parameters(self):
        """Test count_parameters function."""
        model = ResNet18Regression(
            num_outputs=1,
            pretrained=False,
            dropout_rate=0.3
        )
        
        param_count = count_parameters(model)
        
        assert isinstance(param_count, int)
        assert param_count > 0

