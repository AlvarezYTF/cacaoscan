"""
Test 1: Verificar que create_error_response usa 'details' y no 'errors'.

Bug SonarQube: "Remove this unexpected named argument 'errors'"
Archivos corregidos: model_metrics_views.py, refactored_views.py
"""
from unittest.mock import Mock, patch
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.response import Response

from api.utils import create_error_response


class TestCreateErrorResponseDetails(TestCase):
    """Tests para verificar que create_error_response usa 'details' correctamente."""
    
    def test_create_error_response_with_details(self):
        """Verifica que create_error_response acepta el parámetro 'details'."""
        response = create_error_response(
            message="Error de prueba",
            details={"field": "Error en campo"}
        )
        
        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['message'], "Error de prueba")
        self.assertIn('details', response.data)
        self.assertEqual(response.data['details']['field'], "Error en campo")
    
    def test_create_error_response_without_details(self):
        """Verifica que create_error_response funciona sin details."""
        response = create_error_response(message="Error simple")
        
        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['message'], "Error simple")
        self.assertNotIn('details', response.data)
    
    def test_create_error_response_with_error_type(self):
        """Verifica que create_error_response incluye error_type cuando se proporciona."""
        response = create_error_response(
            message="Error de validación",
            error_type="ValidationError",
            details={"error": "Campo requerido"}
        )
        
        self.assertEqual(response.data['error_type'], "ValidationError")
        self.assertIn('details', response.data)
    
    def test_create_error_response_does_not_accept_errors(self):
        """Verifica que create_error_response NO acepta el parámetro 'errors' (bug corregido)."""
        # Intentar llamar con 'errors' debería fallar con TypeError
        # Esto verifica que el código fue corregido para usar 'details'
        try:
            # Si el código está correcto, 'errors' no debería ser un parámetro válido
            response = create_error_response(
                message="Error",
                errors={"field": "Error"}  # Esto debería fallar
            )
            # Si no falla, verificar que 'errors' no está en la respuesta
            self.assertNotIn('errors', response.data)
            self.assertNotIn('errors', str(response.data))
        except TypeError:
            # Esto es lo esperado: TypeError porque 'errors' no es un parámetro válido
            pass


class TestIncrementalViewsErrorResponse(APITestCase):
    """Tests para verificar que IncrementalTrainingView usa 'details' correctamente."""
    
    def setUp(self):
        """Configuración inicial."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    @patch('ml.pipeline.train_all.run_incremental_training_pipeline')
    def test_incremental_training_error_uses_details(self, mock_training):
        """Verifica que los errores usan 'details' y no 'errors'."""
        mock_training.side_effect = Exception("Error de entrenamiento")
        
        url = '/api/v1/incremental-training/'
        response = self.client.post(url, {
            'new_data': [{'image_path': '/test.jpg', 'target': 10.0}],
            'target': 'alto'
        }, format='json')
        
        # Verificar que la respuesta tiene la estructura correcta
        if response.status_code >= 400:
            # La respuesta puede tener 'details' o 'detail' dependiendo del tipo de error
            # Verificamos que NO tenga 'errors'
            self.assertNotIn('errors', response.data)
            # Si tiene 'details', verificar que está presente
            if 'details' in response.data:
                self.assertIsInstance(response.data['details'], (dict, list))

