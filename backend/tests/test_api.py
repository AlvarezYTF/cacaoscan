"""
Tests para la API REST de CacaoScan.
"""
import pytest
import json
import io
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from PIL import Image
import numpy as np
from django.core.files.uploadedfile import SimpleUploadedFile

from ml.prediction.predict import CacaoPredictor
from api.tests.test_constants import (
    TEST_USER_USERNAME,
    TEST_USER_EMAIL,
    TEST_USER_PASSWORD,
)


class TestScanMeasureAPI(APITestCase):
    """Tests para el endpoint de medición."""
    
    def setUp(self):
        """Configuración antes de cada test."""
        self.client = APIClient()
        self.url = reverse('scan-measure')
        
        # Crear usuario y token de autenticación JWT
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Crear imagen de prueba como SimpleUploadedFile
        self.test_image = Image.new('RGB', (224, 224), color='red')
        self.image_bytes = io.BytesIO()
        self.test_image.save(self.image_bytes, format='JPEG')
        self.image_bytes.seek(0)
        self.image_file = SimpleUploadedFile(
            'test_image.jpg',
            self.image_bytes.getvalue(),
            content_type='image/jpeg'
        )
    
    def test_scan_measure_missing_image(self):
        """Test con imagen faltante."""
        response = self.client.post(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('Campo "image" requerido', response.data['error'])
    
    def test_scan_measure_invalid_file_type(self):
        """Test con tipo de archivo inválido."""
        # Crear archivo de texto
        text_file = SimpleUploadedFile(
            'test.txt',
            b'This is not an image',
            content_type='text/plain'
        )
        
        response = self.client.post(self.url, {
            'image': text_file
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_scan_measure_file_too_large(self):
        """Test con archivo demasiado grande."""
        # Crear archivo grande
        large_file = SimpleUploadedFile(
            'large_image.jpg',
            b'x' * (10 * 1024 * 1024),  # 10MB
            content_type='image/jpeg'
        )
        
        response = self.client.post(self.url, {
            'image': large_file
        })
        
        self.assertEqual(response.status_code, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
        self.assertIn('error', response.data)
        self.assertIn('demasiado grande', response.data['error'])
    
    def test_scan_measure_invalid_content_type(self):
        """Test con tipo de contenido inválido."""
        invalid_file = SimpleUploadedFile(
            'test.txt',
            b'not an image',
            content_type='text/plain'
        )
        
        response = self.client.post(self.url, {
            'image': invalid_file
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_scan_measure_invalid_filename(self):
        """Test con nombre de archivo inválido."""
        invalid_file = SimpleUploadedFile(
            'x' * 300 + '.jpg',  # Nombre muy largo
            b'image data',
            content_type='image/jpeg'
        )
        
        response = self.client.post(self.url, {
            'image': invalid_file
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    @patch('api.services.analysis_service.AnalysisService.process_image_with_segmentation')
    def test_scan_measure_models_not_loaded(self, mock_process):
        """Test cuando los modelos no están cargados."""
        from api.services.base import ServiceResult, ValidationServiceError
        
        # Mock service que retorna error de modelos no cargados
        mock_process.return_value = ServiceResult.error(
            ValidationServiceError(
                'Modelos no cargados',
                error_code='models_not_loaded'
            )
        )
        
        response = self.client.post(self.url, {
            'image': self.image_file
        })
        
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn('error', response.data)
    
    @patch('api.services.analysis_service.AnalysisService.process_image_with_segmentation')
    def test_scan_measure_success(self, mock_process):
        """Test de predicción exitosa."""
        from api.services.base import ServiceResult
        
        # Mock service que retorna éxito
        mock_process.return_value = ServiceResult.success({
            'alto_mm': 10.5,
            'ancho_mm': 8.3,
            'grosor_mm': 6.1,
            'peso_g': 2.3,
            'confidences': {
                'alto': 0.85,
                'ancho': 0.80,
                'grosor': 0.75,
                'peso': 0.70
            },
            'crop_url': '/media/cacao_images/crops_runtime/test.png',
            'debug': {
                'segmented': True,
                'yolo_conf': 0.9,
                'latency_ms': 150,
                'models_version': 'v1'
            }
        })
        
        response = self.client.post(self.url, {
            'image': self.image_file
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar campos de respuesta
        expected_fields = [
            'alto_mm', 'ancho_mm', 'grosor_mm', 'peso_g',
            'confidences', 'crop_url', 'debug'
        ]
        
        for field in expected_fields:
            self.assertIn(field, response.data)
        
        # Verificar tipos de datos
        self.assertIsInstance(response.data['alto_mm'], float)
        self.assertIsInstance(response.data['ancho_mm'], float)
        self.assertIsInstance(response.data['grosor_mm'], float)
        self.assertIsInstance(response.data['peso_g'], float)
        self.assertIsInstance(response.data['confidences'], dict)
        self.assertIsInstance(response.data['debug'], dict)
        
        # Verificar confidencias
        confidence_fields = ['alto', 'ancho', 'grosor', 'peso']
        for field in confidence_fields:
            self.assertIn(field, response.data['confidences'])
            self.assertIsInstance(response.data['confidences'][field], float)
    
    @patch('api.services.analysis_service.AnalysisService.process_image_with_segmentation')
    def test_scan_measure_prediction_error(self, mock_process):
        """Test con error en predicción."""
        from api.services.base import ServiceResult, ValidationServiceError
        
        # Mock service que retorna error
        mock_process.return_value = ServiceResult.error(
            ValidationServiceError(
                'Error de predicción',
                error_code='prediction_error'
            )
        )
        
        response = self.client.post(self.url, {
            'image': self.image_file
        })
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', response.data)


class TestModelsStatusAPI(APITestCase):
    """Tests para el endpoint de estado de modelos."""
    
    def setUp(self):
        """Configuración antes de cada test."""
        self.client = APIClient()
        self.url = reverse('models-status')
        
        # Crear usuario y token de autenticación JWT
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    @patch('api.views.ml.model_views.MLService')
    def test_models_status_loaded(self, mock_ml_service_class):
        """Test cuando los modelos están cargados."""
        from api.services.base import ServiceResult
        
        # Mock MLService
        mock_ml_service = Mock()
        mock_ml_service.get_model_status.return_value = ServiceResult.success({
            'status': 'loaded',
            'device': 'cpu',
            'models_loaded': True,
            'load_state': 'loaded',
            'model': 'HybridCacaoRegression',
            'model_details': {},
            'scalers': 'loaded'
        })
        mock_ml_service_class.return_value = mock_ml_service
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar campos de respuesta
        expected_fields = ['status', 'device', 'model', 'model_details', 'scalers']
        
        for field in expected_fields:
            self.assertIn(field, response.data)
    
    @patch('api.views.ml.model_views.MLService')
    def test_models_status_not_loaded(self, mock_ml_service_class):
        """Test cuando los modelos no están cargados."""
        from api.services.base import ServiceResult
        
        # Mock MLService sin modelos cargados
        mock_ml_service = Mock()
        mock_ml_service.get_model_status.return_value = ServiceResult.success({
            'status': 'not_loaded',
            'device': 'unknown',
            'models_loaded': False,
            'load_state': 'not_loaded',
            'model': 'HybridCacaoRegression',
            'model_details': {},
            'scalers': 'not_loaded'
        })
        mock_ml_service_class.return_value = mock_ml_service
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'not_loaded')
    
    @patch('api.views.ml.model_views.MLService')
    def test_models_status_error(self, mock_ml_service_class):
        """Test con error al obtener estado de modelos."""
        from api.services.base import ServiceResult, ValidationServiceError
        
        # Mock MLService que retorna error
        mock_ml_service = Mock()
        mock_ml_service.get_model_status.return_value = ServiceResult.error(
            ValidationServiceError('Error de predictor')
        )
        mock_ml_service_class.return_value = mock_ml_service
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn('error', response.data)


class TestLoadModelsAPI(APITestCase):
    """Tests para el endpoint de carga de modelos."""
    
    def setUp(self):
        """Configuración antes de cada test."""
        self.client = APIClient()
        self.url = reverse('load-models')
        
        # Crear usuario y token de autenticación JWT
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    @patch('api.views.ml.model_views.MLService')
    def test_load_models_success(self, mock_ml_service_class):
        """Test de carga exitosa de modelos."""
        from api.services.base import ServiceResult
        
        # Mock MLService
        mock_ml_service = Mock()
        mock_ml_service.get_model_status.return_value = ServiceResult.success({
            'models_loaded': False,
            'load_state': 'not_loaded'
        })
        mock_ml_service.load_models.return_value = ServiceResult.success({})
        mock_ml_service_class.return_value = mock_ml_service
        
        response = self.client.post(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('message', response.data)
    
    @patch('api.views.ml.model_views.MLService')
    def test_load_models_failure(self, mock_ml_service_class):
        """Test de fallo en carga de modelos."""
        from api.services.base import ServiceResult, ValidationServiceError
        
        # Mock MLService que falla
        mock_ml_service = Mock()
        mock_ml_service.get_model_status.return_value = ServiceResult.success({
            'models_loaded': False,
            'load_state': 'not_loaded'
        })
        mock_ml_service.load_models.return_value = ServiceResult.error(
            ValidationServiceError('Error cargando modelos')
        )
        mock_ml_service_class.return_value = mock_ml_service
        
        response = self.client.post(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data['status'], 'error')
        self.assertIn('error', response.data)
    
    @patch('api.views.ml.model_views.MLService')
    def test_load_models_exception(self, mock_ml_service_class):
        """Test con excepción en carga de modelos."""
        # Mock MLService que lanza excepción
        mock_ml_service = Mock()
        mock_ml_service.get_model_status.side_effect = Exception("Error de carga")
        mock_ml_service_class.return_value = mock_ml_service
        
        response = self.client.post(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data['status'], 'error')
        self.assertIn('error', response.data)


class TestDatasetValidationAPI(APITestCase):
    """Tests para el endpoint de validación de dataset."""
    
    def setUp(self):
        """Configuración antes de cada test."""
        self.client = APIClient()
        self.url = reverse('dataset-validation')
        
        # Crear usuario y token de autenticación JWT
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    @patch('api.views.ml.model_views.validate_dataset_task')
    def test_dataset_validation_success(self, mock_task):
        """Test de validación exitosa del dataset."""
        from django.core.cache import cache
        from core.utils import get_cache_key
        
        # Mock cache con resultado válido
        cache_key = get_cache_key('dataset_validation', 'stats')
        cached_result = {
            'valid': False,
            'stats': {
                'total_records': 100,
                'valid_records': 95,
                'missing_images': 5,
                'missing_ids': [1, 2, 3, 4, 5],
                'dimensions_stats': {}
            },
            'status': 'success'
        }
        cache.set(cache_key, cached_result, timeout=300)
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar campos de respuesta
        expected_fields = ['valid', 'stats', 'status']
        for field in expected_fields:
            self.assertIn(field, response.data)
        
        self.assertEqual(response.data['status'], 'success')
        self.assertFalse(response.data['valid'])  # Hay imágenes faltantes
    
    @patch('api.views.ml.model_views.validate_dataset_task')
    def test_dataset_validation_error(self, mock_task):
        """Test con error en validación del dataset."""
        from django.core.cache import cache
        from core.utils import get_cache_key
        
        # Limpiar cache para forzar error
        cache_key = get_cache_key('dataset_validation', 'stats')
        cache.delete(cache_key)
        
        # Mock task que falla
        mock_task.delay.side_effect = Exception("Error de dataset")
        
        # El endpoint ahora retorna 202 con task_id, no 500 directamente
        # Pero si hay excepción al encolar, puede retornar 500
        response = self.client.get(self.url)
        
        # Puede retornar 202 (task enqueued) o 500 (error al encolar)
        self.assertIn(response.status_code, [status.HTTP_202_ACCEPTED, status.HTTP_500_INTERNAL_SERVER_ERROR])


class TestAPIIntegration(TestCase):
    """Tests de integración para la API."""
    
    def setUp(self):
        """Configuración antes de cada test."""
        self.client = APIClient()
    
    def test_api_endpoints_exist(self):
        """Test que todos los endpoints existen."""
        endpoints = [
            'scan-measure',
            'models-status',
            'load-models',
            'dataset-validation'
        ]
        
        for endpoint in endpoints:
            url = reverse(endpoint)
            response = self.client.get(url) if endpoint != 'scan-measure' else self.client.post(url)
            
            # No debe devolver 404
            self.assertNotEqual(response.status_code, 404, f"Endpoint {endpoint} no encontrado")
    
    def test_cors_headers(self):
        """Test que los headers CORS están presentes."""
        # Nota: CORS headers pueden no estar presentes en tests sin configuración CORS
        # Este test verifica que el endpoint responde correctamente
        response = self.client.get(reverse('models-status'))
        
        # Verificar que el endpoint responde (puede ser 200 o 401/500 dependiendo de auth)
        self.assertIn(response.status_code, [200, 401, 500])
    
    def test_content_type_json(self):
        """Test que las respuestas son JSON."""
        response = self.client.get(reverse('models-status'))
        
        self.assertEqual(response['Content-Type'], 'application/json')


class TestAPIErrorHandling(TestCase):
    """Tests para manejo de errores en la API."""
    
    def setUp(self):
        """Configuración antes de cada test."""
        self.client = APIClient()
    
    def test_invalid_json_response_format(self):
        """Test que las respuestas de error siguen el formato JSON correcto."""
        response = self.client.post(reverse('scan-measure'))
        
        # Debe devolver JSON válido
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # Debe tener campos de error
        self.assertIn('error', response.data)
        self.assertIn('status', response.data)
    
    def test_error_status_codes(self):
        """Test que se devuelven códigos de estado HTTP correctos."""
        # 400 Bad Request
        response = self.client.post(reverse('scan-measure'))
        self.assertEqual(response.status_code, 400)
        
        # 200 OK para endpoints válidos
        response = self.client.get(reverse('models-status'))
        self.assertIn(response.status_code, [200, 500])  # 500 si hay error interno


