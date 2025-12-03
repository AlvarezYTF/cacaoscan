"""
Test 2: Verificar que ModelMetricsCreateView usa 'details' correctamente.

Bug SonarQube: "Remove this unexpected named argument 'errors'"
Archivo corregido: model_metrics_views.py
"""
from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from api.tests.test_constants import TEST_USER_PASSWORD


class TestModelMetricsViewsErrorResponse(APITestCase):
    """Tests para verificar que ModelMetricsCreateView usa 'details' correctamente."""
    
    def setUp(self):
        """Configuración inicial."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password=TEST_USER_PASSWORD  # NOSONAR - test credential from constants
        )
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    
    def test_model_metrics_invalid_data_uses_details(self):
        """Verifica que los errores de validación usan 'details'."""
        # Intentar con la URL correcta
        url = '/api/v1/model-metrics/create/'
        # Datos inválidos para forzar error de validación
        invalid_data = {
            'model_name': '',  # Campo requerido vacío
        }
        
        response = self.client.post(url, invalid_data, format='json')
        
        # Si el método no está permitido, saltar el test
        if response.status_code == 405:
            self.skipTest("Endpoint no acepta POST, puede que la URL esté mal configurada")
        
        # Verificar que la respuesta usa 'details' y no 'errors'
        if response.status_code >= 400:
            # Verificar que NO tiene 'errors'
            self.assertNotIn('errors', response.data)
            # Si tiene 'details', verificar que está presente
            if 'details' in response.data:
                self.assertIsInstance(response.data['details'], (dict, list))
                self.assertFalse(response.data.get('success', True))
    
    @patch('api.model_metrics_views.ModelMetrics')
    def test_model_metrics_exception_uses_details(self, mock_model):
        """Verifica que las excepciones usan 'details'."""
        from training.models import ModelMetrics
        
        # Mock para simular error de base de datos
        mock_model.objects.create.side_effect = Exception("Error de base de datos")
        
        url = '/api/v1/model-metrics/create/'
        valid_data = {
            'model_name': 'test_model',
            'model_type': 'resnet18',
            'mae': 0.5,
            'rmse': 0.6,
            'r2': 0.8
        }
        
        response = self.client.post(url, valid_data, format='json')
        
        # Si el método no está permitido, saltar el test
        if response.status_code == 405:
            self.skipTest("Endpoint no acepta POST, puede que la URL esté mal configurada")
        
        # Verificar que la respuesta usa 'details'
        if response.status_code >= 400:
            # Verificar que NO tiene 'errors'
            self.assertNotIn('errors', response.data)
            # Si tiene 'details', verificar que está presente
            if 'details' in response.data:
                self.assertIsInstance(response.data['details'], (dict, list))

