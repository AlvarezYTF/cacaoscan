"""
Unit tests for regression models (models.py).
Tests model creation, forward pass, and model utilities.
"""
import pytest
import torch
from unittest.mock import patch, MagicMock

from ml.regression.models import (
    ResNet18Regression,
    ConvNeXtTinyRegression,
    MultiHeadRegression,
    HybridCacaoRegression,
    create_model,
    get_model_info,
    count_parameters,
    TARGETS,
    TARGET_NAMES
)


@pytest.fixture
def sample_image_batch():
    """Create sample image batch for testing."""
    return torch.randn(2, 3, 224, 224)


@pytest.fixture
def sample_pixel_features():
    """Create sample pixel features for testing."""
    return torch.randn(2, 10)


class TestResNet18Regression:
    """Tests for ResNet18Regression model."""
    
    def test_initialization_default(self):
        """Test ResNet18Regression initialization with defaults."""
        model = ResNet18Regression()
        
        assert model.num_outputs == 1
        assert model.backbone is not None
    
    def test_initialization_custom_outputs(self):
        """Test ResNet18Regression with custom num_outputs."""
        model = ResNet18Regression(num_outputs=4)
        
        assert model.num_outputs == 4
    
    def test_initialization_pretrained_false(self):
        """Test ResNet18Regression with pretrained=False."""
        model = ResNet18Regression(pretrained=False)
        
        assert model.backbone is not None
    
    def test_forward_pass(self, sample_image_batch):
        """Test forward pass of ResNet18Regression."""
        model = ResNet18Regression(num_outputs=1, pretrained=False)
        model.eval()
        
        with torch.no_grad():
            output = model(sample_image_batch)
        
        assert output.shape == (2, 1)  # batch_size, num_outputs
    
    def test_forward_pass_multiple_outputs(self, sample_image_batch):
        """Test forward pass with multiple outputs."""
        model = ResNet18Regression(num_outputs=4, pretrained=False)
        model.eval()
        
        with torch.no_grad():
            output = model(sample_image_batch)
        
        assert output.shape == (2, 4)
    
    def test_get_features(self, sample_image_batch):
        """Test get_features method."""
        model = ResNet18Regression(pretrained=False)
        model.eval()
        
        with torch.no_grad():
            features = model.get_features(sample_image_batch)
        
        assert features.shape[0] == 2  # batch_size
        assert features.shape[1] == 512  # ResNet18 features


class TestConvNeXtTinyRegression:
    """Tests for ConvNeXtTinyRegression model."""
    
    @pytest.mark.skipif(
        not hasattr(__import__('sys').modules.get('timm', None), 'create_model'),
        reason="timm not available"
    )
    def test_initialization_default(self):
        """Test ConvNeXtTinyRegression initialization."""
        try:
            model = ConvNeXtTinyRegression(pretrained=False)
            assert model.num_outputs == 1
        except ImportError:
            pytest.skip("timm not available")
    
    @pytest.mark.skipif(
        not hasattr(__import__('sys').modules.get('timm', None), 'create_model'),
        reason="timm not available"
    )
    def test_forward_pass(self, sample_image_batch):
        """Test forward pass of ConvNeXtTinyRegression."""
        try:
            model = ConvNeXtTinyRegression(pretrained=False)
            model.eval()
            
            with torch.no_grad():
                output = model(sample_image_batch)
            
            assert output.shape[0] == 2  # batch_size
            assert output.shape[1] == 1  # num_outputs
        except ImportError:
            pytest.skip("timm not available")
    
    def test_initialization_timm_not_available(self):
        """Test that ImportError is raised when timm is not available."""
        with patch('ml.regression.models.TIMM_AVAILABLE', False):
            with pytest.raises(ImportError, match="timm es requerido"):
                ConvNeXtTinyRegression()


class TestMultiHeadRegression:
    """Tests for MultiHeadRegression model."""
    
    def test_initialization_resnet18_backbone(self):
        """Test MultiHeadRegression with ResNet18 backbone."""
        model = MultiHeadRegression(backbone_type="resnet18", pretrained=False)
        
        assert model.backbone_type == "resnet18"
        assert 'alto' in model.heads
        assert 'ancho' in model.heads
        assert 'grosor' in model.heads
        assert 'peso' in model.heads
    
    def test_forward_pass_dict_output(self, sample_image_batch):
        """Test forward pass returns dictionary."""
        model = MultiHeadRegression(backbone_type="resnet18", pretrained=False)
        model.eval()
        
        with torch.no_grad():
            output = model(sample_image_batch)
        
        assert isinstance(output, dict)
        assert 'alto' in output
        assert 'ancho' in output
        assert 'grosor' in output
        assert 'peso' in output
        assert output['alto'].shape == (2, 1)
    
    def test_forward_single_target(self, sample_image_batch):
        """Test forward_single method."""
        model = MultiHeadRegression(backbone_type="resnet18", pretrained=False)
        model.eval()
        
        with torch.no_grad():
            output = model.forward_single(sample_image_batch, target='alto')
        
        assert output.shape == (2, 1)
    
    def test_initialization_invalid_backbone(self):
        """Test MultiHeadRegression with invalid backbone type."""
        with pytest.raises(ValueError, match="no soportado"):
            MultiHeadRegression(backbone_type="invalid", pretrained=False)


class TestHybridCacaoRegression:
    """Tests for HybridCacaoRegression model."""
    
    @pytest.mark.skipif(
        not hasattr(__import__('sys').modules.get('timm', None), 'create_model'),
        reason="timm not available"
    )
    def test_initialization_default(self):
        """Test HybridCacaoRegression initialization."""
        try:
            model = HybridCacaoRegression(pretrained=False, use_pixel_features=True)
            assert model.num_outputs == 4
            assert model.use_pixel_features is True
        except ImportError:
            pytest.skip("timm not available")
    
    @pytest.mark.skipif(
        not hasattr(__import__('sys').modules.get('timm', None), 'create_model'),
        reason="timm not available"
    )
    def test_forward_pass_with_pixel_features(self, sample_image_batch, sample_pixel_features):
        """Test forward pass with pixel features."""
        try:
            model = HybridCacaoRegression(
                pretrained=False,
                use_pixel_features=True,
                num_pixel_features=10
            )
            model.eval()
            
            with torch.no_grad():
                output = model(sample_image_batch, sample_pixel_features)
            
            assert isinstance(output, dict)
            assert 'alto' in output
            assert output['alto'].shape == (2, 1)
        except ImportError:
            pytest.skip("timm not available")
    
    @pytest.mark.skipif(
        not hasattr(__import__('sys').modules.get('timm', None), 'create_model'),
        reason="timm not available"
    )
    def test_forward_pass_without_pixel_features(self, sample_image_batch):
        """Test forward pass without pixel features."""
        try:
            model = HybridCacaoRegression(
                pretrained=False,
                use_pixel_features=False
            )
            model.eval()
            
            with torch.no_grad():
                output = model(sample_image_batch, pixel_features=None)
            
            assert isinstance(output, dict)
        except ImportError:
            pytest.skip("timm not available")
    
    def test_initialization_timm_not_available(self):
        """Test that ImportError is raised when timm is not available."""
        with patch('ml.regression.models.TIMM_AVAILABLE', False):
            with pytest.raises(ImportError, match="timm es requerido"):
                HybridCacaoRegression()


class TestCreateModel:
    """Tests for create_model function."""
    
    def test_create_model_resnet18(self):
        """Test creating ResNet18 model."""
        model = create_model(
            model_type="resnet18",
            num_outputs=1,
            pretrained=False
        )
        
        assert isinstance(model, ResNet18Regression)
        assert model.num_outputs == 1
    
    def test_create_model_multi_head(self):
        """Test creating multi-head model."""
        model = create_model(
            model_type="resnet18",
            multi_head=True,
            pretrained=False
        )
        
        assert isinstance(model, MultiHeadRegression)
    
    @pytest.mark.skipif(
        not hasattr(__import__('sys').modules.get('timm', None), 'create_model'),
        reason="timm not available"
    )
    def test_create_model_hybrid(self):
        """Test creating hybrid model."""
        try:
            model = create_model(
                model_type="resnet18",
                hybrid=True,
                pretrained=False,
                use_pixel_features=True
            )
            
            assert isinstance(model, HybridCacaoRegression)
        except ImportError:
            pytest.skip("timm not available")
    
    def test_create_model_invalid_type(self):
        """Test creating model with invalid type."""
        with pytest.raises(ValueError, match="no soportado"):
            create_model(model_type="invalid", pretrained=False)


class TestModelUtilities:
    """Tests for model utility functions."""
    
    def test_get_model_info(self):
        """Test get_model_info function."""
        model = ResNet18Regression(pretrained=False)
        
        info = get_model_info(model)
        
        assert 'total_parameters' in info
        assert 'trainable_parameters' in info
        assert 'model_type' in info
        assert 'device' in info
        assert info['model_type'] == 'ResNet18Regression'
        assert info['total_parameters'] > 0
    
    def test_count_parameters(self):
        """Test count_parameters function."""
        model = ResNet18Regression(pretrained=False)
        
        param_count = count_parameters(model)
        
        assert param_count > 0
        assert isinstance(param_count, int)
    
    def test_targets_constant(self):
        """Test that TARGETS constant is defined."""
        assert TARGETS == ['alto', 'ancho', 'grosor', 'peso']
        assert len(TARGETS) == 4
    
    def test_target_names_constant(self):
        """Test that TARGET_NAMES constant is defined."""
        assert 'alto' in TARGET_NAMES
        assert 'ancho' in TARGET_NAMES
        assert 'grosor' in TARGET_NAMES
        assert 'peso' in TARGET_NAMES
        assert all(isinstance(v, str) for v in TARGET_NAMES.values())

