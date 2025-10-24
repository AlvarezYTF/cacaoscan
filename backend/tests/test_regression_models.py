"""
Tests para los modelos de regresión.
"""
import pytest
import torch
import numpy as np
from unittest.mock import Mock, patch

from ml.regression.models import (
    ResNet18Regression,
    ConvNeXtTinyRegression,
    MultiHeadRegression,
    create_model,
    get_model_info,
    count_parameters,
    TARGETS
)


class TestResNet18Regression:
    """Tests para ResNet18Regression."""
    
    def test_init_single_output(self):
        """Test de inicialización con una salida."""
        model = ResNet18Regression(num_outputs=1)
        assert model.num_outputs == 1
        
        # Test forward pass
        x = torch.randn(2, 3, 224, 224)
        output = model(x)
        assert output.shape == (2, 1)
    
    def test_init_multiple_outputs(self):
        """Test de inicialización con múltiples salidas."""
        model = ResNet18Regression(num_outputs=4)
        assert model.num_outputs == 4
        
        # Test forward pass
        x = torch.randn(2, 3, 224, 224)
        output = model(x)
        assert output.shape == (2, 4)
    
    def test_get_features(self):
        """Test de extracción de características."""
        model = ResNet18Regression(num_outputs=1)
        x = torch.randn(2, 3, 224, 224)
        
        features = model.get_features(x)
        assert features.shape[0] == 2  # Batch size
        assert features.shape[1] == 512  # Feature dimension
    
    def test_dropout_rate(self):
        """Test con diferentes tasas de dropout."""
        model = ResNet18Regression(num_outputs=1, dropout_rate=0.5)
        x = torch.randn(2, 3, 224, 224)
        
        # Debe funcionar sin errores
        output = model(x)
        assert output.shape == (2, 1)


class TestConvNeXtTinyRegression:
    """Tests para ConvNeXtTinyRegression."""
    
    @pytest.mark.skipif(True, reason="timm no está disponible en tests")
    def test_init_single_output(self):
        """Test de inicialización con una salida."""
        model = ConvNeXtTinyRegression(num_outputs=1)
        assert model.num_outputs == 1
        
        # Test forward pass
        x = torch.randn(2, 3, 224, 224)
        output = model(x)
        assert output.shape == (2, 1)
    
    @pytest.mark.skipif(True, reason="timm no está disponible en tests")
    def test_get_features(self):
        """Test de extracción de características."""
        model = ConvNeXtTinyRegression(num_outputs=1)
        x = torch.randn(2, 3, 224, 224)
        
        features = model.get_features(x)
        assert features.shape[0] == 2  # Batch size
    
    def test_timm_not_available(self):
        """Test cuando timm no está disponible."""
        with patch('ml.regression.models.TIMM_AVAILABLE', False):
            with pytest.raises(ImportError, match="timm es requerido"):
                ConvNeXtTinyRegression(num_outputs=1)


class TestMultiHeadRegression:
    """Tests para MultiHeadRegression."""
    
    def test_init_resnet18(self):
        """Test de inicialización con ResNet18."""
        model = MultiHeadRegression(backbone_type="resnet18")
        
        # Test forward pass
        x = torch.randn(2, 3, 224, 224)
        outputs = model(x)
        
        assert isinstance(outputs, dict)
        for target in TARGETS:
            assert target in outputs
            assert outputs[target].shape == (2, 1)
    
    @pytest.mark.skipif(True, reason="timm no está disponible en tests")
    def test_init_convnext_tiny(self):
        """Test de inicialización con ConvNeXt Tiny."""
        model = MultiHeadRegression(backbone_type="convnext_tiny")
        
        # Test forward pass
        x = torch.randn(2, 3, 224, 224)
        outputs = model(x)
        
        assert isinstance(outputs, dict)
        for target in TARGETS:
            assert target in outputs
            assert outputs[target].shape == (2, 1)
    
    def test_forward_single(self):
        """Test de forward pass para un target específico."""
        model = MultiHeadRegression(backbone_type="resnet18")
        x = torch.randn(2, 3, 224, 224)
        
        for target in TARGETS:
            output = model.forward_single(x, target)
            assert output.shape == (2, 1)
    
    def test_invalid_backbone(self):
        """Test con backbone inválido."""
        with pytest.raises(ValueError, match="Backbone tipo"):
            MultiHeadRegression(backbone_type="invalid_backbone")


class TestCreateModel:
    """Tests para la función create_model."""
    
    def test_create_resnet18_single(self):
        """Test de creación de ResNet18 individual."""
        model = create_model(
            model_type="resnet18",
            num_outputs=1,
            multi_head=False
        )
        
        assert isinstance(model, ResNet18Regression)
        assert model.num_outputs == 1
        
        # Test forward pass
        x = torch.randn(2, 3, 224, 224)
        output = model(x)
        assert output.shape == (2, 1)
    
    def test_create_multi_head(self):
        """Test de creación de modelo multi-head."""
        model = create_model(
            model_type="resnet18",
            multi_head=True
        )
        
        assert isinstance(model, MultiHeadRegression)
        
        # Test forward pass
        x = torch.randn(2, 3, 224, 224)
        outputs = model(x)
        
        assert isinstance(outputs, dict)
        for target in TARGETS:
            assert target in outputs
            assert outputs[target].shape == (2, 1)
    
    def test_create_invalid_model_type(self):
        """Test con tipo de modelo inválido."""
        with pytest.raises(ValueError, match="Tipo de modelo"):
            create_model(model_type="invalid_model")


class TestModelUtilities:
    """Tests para utilidades de modelos."""
    
    def test_get_model_info(self):
        """Test de obtención de información del modelo."""
        model = ResNet18Regression(num_outputs=1)
        info = get_model_info(model)
        
        assert 'total_parameters' in info
        assert 'trainable_parameters' in info
        assert 'model_type' in info
        assert 'device' in info
        
        assert info['model_type'] == 'ResNet18Regression'
        assert info['total_parameters'] > 0
        assert info['trainable_parameters'] > 0
    
    def test_count_parameters(self):
        """Test de conteo de parámetros."""
        model = ResNet18Regression(num_outputs=1)
        param_count = count_parameters(model)
        
        assert param_count > 0
        assert isinstance(param_count, int)
    
    def test_model_device(self):
        """Test de dispositivo del modelo."""
        model = ResNet18Regression(num_outputs=1)
        
        # Modelo debe estar en CPU por defecto
        device = next(model.parameters()).device
        assert device.type == 'cpu'
        
        # Mover a GPU si está disponible
        if torch.cuda.is_available():
            model = model.cuda()
            device = next(model.parameters()).device
            assert device.type == 'cuda'


class TestModelSmokeTests:
    """Smoke tests para verificar que los modelos funcionan."""
    
    def test_resnet18_smoke(self):
        """Smoke test para ResNet18."""
        model = ResNet18Regression(num_outputs=1)
        model.eval()
        
        # Test con batch de diferentes tamaños
        for batch_size in [1, 2, 4]:
            x = torch.randn(batch_size, 3, 224, 224)
            
            with torch.no_grad():
                output = model(x)
                assert output.shape == (batch_size, 1)
                assert not torch.isnan(output).any()
                assert not torch.isinf(output).any()
    
    def test_multi_head_smoke(self):
        """Smoke test para modelo multi-head."""
        model = MultiHeadRegression(backbone_type="resnet18")
        model.eval()
        
        # Test con batch de diferentes tamaños
        for batch_size in [1, 2, 4]:
            x = torch.randn(batch_size, 3, 224, 224)
            
            with torch.no_grad():
                outputs = model(x)
                
                for target in TARGETS:
                    assert target in outputs
                    assert outputs[target].shape == (batch_size, 1)
                    assert not torch.isnan(outputs[target]).any()
                    assert not torch.isinf(outputs[target]).any()
    
    def test_model_gradients(self):
        """Test de gradientes en modelos."""
        model = ResNet18Regression(num_outputs=1)
        model.train()
        
        x = torch.randn(2, 3, 224, 224, requires_grad=True)
        target = torch.randn(2, 1)
        
        output = model(x)
        loss = torch.nn.functional.mse_loss(output, target)
        loss.backward()
        
        # Verificar que los gradientes se calcularon
        assert x.grad is not None
        assert x.grad.shape == x.shape
        
        # Verificar que los parámetros del modelo tienen gradientes
        for param in model.parameters():
            if param.requires_grad:
                assert param.grad is not None
