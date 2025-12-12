"""
Tests for deprecated api/serializers.py (re-export module).
"""
import pytest
from api import serializers


class TestDeprecatedSerializersModule:
    """Tests for deprecated serializers module that re-exports from serializers package."""
    
    def test_serializers_module_exists(self):
        """Test that serializers module exists."""
        assert serializers is not None
    
    def test_serializers_re_exports_common(self):
        """Test that common serializers are re-exported."""
        # These should be available from the re-export
        assert hasattr(serializers, 'ErrorResponseSerializer')
        assert hasattr(serializers, 'NotificationSerializer')
    
    def test_serializers_re_exports_auth(self):
        """Test that auth serializers are re-exported."""
        assert hasattr(serializers, 'LoginSerializer')
        assert hasattr(serializers, 'RegisterSerializer')
        assert hasattr(serializers, 'UserSerializer')
    
    def test_serializers_re_exports_image(self):
        """Test that image serializers are re-exported."""
        assert hasattr(serializers, 'CacaoImageSerializer')
        assert hasattr(serializers, 'CacaoPredictionSerializer')
    
    def test_serializers_re_exports_finca(self):
        """Test that finca serializers are re-exported."""
        assert hasattr(serializers, 'FincaSerializer')
        assert hasattr(serializers, 'LoteSerializer')
    
    def test_serializers_re_exports_ml(self):
        """Test that ML serializers are re-exported."""
        assert hasattr(serializers, 'TrainingJobSerializer')
        assert hasattr(serializers, 'ModelMetricsSerializer')

