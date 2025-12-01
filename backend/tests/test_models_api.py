"""
Unit tests for api.models (lazy import wrapper).
Tests cover lazy import functionality and backward compatibility.
"""
import pytest
from unittest.mock import patch, MagicMock


class TestApiModelsLazyImport:
    """Tests for api.models lazy import wrapper."""
    
    def test_lazy_import_finca(self):
        """Test lazy import of Finca model."""
        from api.models import Finca
        
        assert Finca is not None
        # Should be the actual model class
        assert hasattr(Finca, '_meta')
    
    def test_lazy_import_lote(self):
        """Test lazy import of Lote model."""
        from api.models import Lote
        
        assert Lote is not None
        assert hasattr(Lote, '_meta')
    
    def test_lazy_import_user_profile(self):
        """Test lazy import of UserProfile model."""
        from api.models import UserProfile
        
        assert UserProfile is not None
        assert hasattr(UserProfile, '_meta')
    
    def test_lazy_import_email_verification_token(self):
        """Test lazy import of EmailVerificationToken model."""
        from api.models import EmailVerificationToken
        
        assert EmailVerificationToken is not None
        assert hasattr(EmailVerificationToken, '_meta')
    
    def test_lazy_import_cacao_image(self):
        """Test lazy import of CacaoImage model."""
        from api.models import CacaoImage
        
        assert CacaoImage is not None
        assert hasattr(CacaoImage, '_meta')
    
    def test_lazy_import_cacao_prediction(self):
        """Test lazy import of CacaoPrediction model."""
        from api.models import CacaoPrediction
        
        assert CacaoPrediction is not None
        assert hasattr(CacaoPrediction, '_meta')
    
    def test_lazy_import_training_job(self):
        """Test lazy import of TrainingJob model."""
        from api.models import TrainingJob
        
        assert TrainingJob is not None
        assert hasattr(TrainingJob, '_meta')
    
    def test_lazy_import_model_metrics(self):
        """Test lazy import of ModelMetrics model."""
        from api.models import ModelMetrics
        
        assert ModelMetrics is not None
        assert hasattr(ModelMetrics, '_meta')
    
    def test_lazy_import_system_settings(self):
        """Test lazy import of SystemSettings model."""
        from api.models import SystemSettings
        
        assert SystemSettings is not None
        assert hasattr(SystemSettings, '_meta')
    
    def test_lazy_import_reporte_generado(self):
        """Test lazy import of ReporteGenerado model."""
        from api.models import ReporteGenerado
        
        assert ReporteGenerado is not None
        assert hasattr(ReporteGenerado, '_meta')
    
    def test_lazy_import_login_history(self):
        """Test lazy import of LoginHistory model."""
        from api.models import LoginHistory
        
        assert LoginHistory is not None
        assert hasattr(LoginHistory, '_meta')
    
    def test_lazy_import_invalid_attribute(self):
        """Test that invalid attribute raises AttributeError."""
        from api.models import InvalidModel
        
        with pytest.raises(AttributeError):
            _ = InvalidModel
    
    def test_lazy_import_caching(self):
        """Test that lazy imports are cached."""
        from api.models import Finca
        
        # First import
        finca1 = Finca
        
        # Second import should return cached version
        from api.models import Finca as Finca2
        
        assert Finca1 is Finca2
    
    def test_lazy_import_backward_compatibility(self):
        """Test that api.models provides backward compatibility."""
        # These imports should work for backward compatibility
        from api.models import (
            Finca,
            Lote,
            UserProfile,
            EmailVerificationToken,
            CacaoImage,
            CacaoPrediction
        )
        
        # All should be importable
        assert all([
            Finca is not None,
            Lote is not None,
            UserProfile is not None,
            EmailVerificationToken is not None,
            CacaoImage is not None,
            CacaoPrediction is not None
        ])
    
    @patch('api.models.get_model_safely')
    def test_lazy_import_error_handling(self, mock_get_model_safely):
        """Test error handling in lazy import."""
        mock_get_model_safely.return_value = None
        
        with pytest.raises(ImportError):
            from api.models import Finca
            _ = Finca

