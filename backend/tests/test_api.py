"""
Tests para la API REST de CacaoScan.
"""
import pytest
import json
import io
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from PIL import Image
import numpy as np

from ml.prediction.predict import CacaoPredictor


class TestScanMeasureAPI(TestCase):
    """Tests para el endpoint de medición."""
    
    def setUp(self):
        """Configuración antes de cada test."""
        self.client = APIClient()
        self.url = reverse('scan-measure')
        
        # Crear imagen de prueba
        self.test_image = Image.new('RGB', (224, 224), color='red')
        self.image_bytes = io.BytesIO()
        self.test_image.save(self.image_bytes, format='JPEG')
        self.image_bytes.seek(0)
    
    def test_scan_measure_missing_image(self):
        """Test con imagen faltante."""
        response = self.client.post(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('Campo "image" requerido', response.data['error'])
    
    def test_scan_measure_invalid_file_type(self):
        """Test con tipo de archivo inválido."""
        # Crear archivo de texto
        text_file = io.StringIO("This is not an image")
        
        response = self.client.post(self.url, {
            'image': text_file
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_scan_measure_file_too_large(self):
        """Test con archivo demasiado grande."""
        # Mock de archivo grande
        large_file = Mock()
        large_file.size = 10 * 1024 * 1024  # 10MB
        large_file.name = 'large_image.jpg'
        large_file.content_type = 'image/jpeg'
        large_file.read.return_value = b'x' * (10 * 1024 * 1024)
        
        response = self.client.post(self.url, {
            'image': large_file
        })
        
        self.assertEqual(response.status_code, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
        self.assertIn('error', response.data)
        self.assertIn('demasiado grande', response.data['error'])
    
    def test_scan_measure_invalid_content_type(self):
        """Test con tipo de contenido inválido."""
        invalid_file = Mock()
        invalid_file.size = 1024
        invalid_file.name = 'test.txt'
        invalid_file.content_type = 'text/plain'
        invalid_file.read.return_value = b'not an image'
        
        response = self.client.post(self.url, {
            'image': invalid_file
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_scan_measure_invalid_filename(self):
        """Test con nombre de archivo inválido."""
        invalid_file = Mock()
        invalid_file.size = 1024
        invalid_file.name = 'x' * 300  # Nombre muy largo
        invalid_file.content_type = 'image/jpeg'
        invalid_file.read.return_value = b'image data'
        
        response = self.client.post(self.url, {
            'image': invalid_file
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    @patch('api.views.get_predictor')
    def test_scan_measure_models_not_loaded(self, mock_get_predictor):
        """Test cuando los modelos no están cargados."""
        # Mock predictor sin modelos cargados
        mock_predictor = Mock()
        mock_predictor.models_loaded = False
        mock_get_predictor.return_value = mock_predictor
        
        response = self.client.post(self.url, {
            'image': self.image_bytes
        })
        
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn('error', response.data)
        self.assertIn('Modelos no cargados', response.data['error'])
    
    @patch('api.views.get_predictor')
    def test_scan_measure_success(self, mock_get_predictor):
        """Test de predicción exitosa."""
        # Mock predictor con modelos cargados
        mock_predictor = Mock()
        mock_predictor.models_loaded = True
        mock_predictor.predict.return_value = {
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
        }
        mock_get_predictor.return_value = mock_predictor
        
        response = self.client.post(self.url, {
            'image': self.image_bytes
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
    
    @patch('api.views.get_predictor')
    def test_scan_measure_prediction_error(self, mock_get_predictor):
        """Test con error en predicción."""
        # Mock predictor que lanza excepción
        mock_predictor = Mock()
        mock_predictor.models_loaded = True
        mock_predictor.predict.side_effect = Exception("Error de predicción")
        mock_get_predictor.return_value = mock_predictor
        
        response = self.client.post(self.url, {
            'image': self.image_bytes
        })
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', response.data)


class TestModelsStatusAPI(TestCase):
    """Tests para el endpoint de estado de modelos."""
    
    def setUp(self):
        """Configuración antes de cada test."""
        self.client = APIClient()
        self.url = reverse('models-status')
    
    @patch('api.views.get_predictor')
    def test_models_status_loaded(self, mock_get_predictor):
        """Test cuando los modelos están cargados."""
        # Mock predictor con modelos cargados
        mock_predictor = Mock()
        mock_predictor.get_model_info.return_value = {
            'status': 'loaded',
            'device': 'cpu',
            'models': {
                'alto': {'type': 'ResNet18Regression', 'parameters': 1000000},
                'ancho': {'type': 'ResNet18Regression', 'parameters': 1000000},
                'grosor': {'type': 'ResNet18Regression', 'parameters': 1000000},
                'peso': {'type': 'ResNet18Regression', 'parameters': 1000000}
            }
        }
        mock_get_predictor.return_value = mock_predictor
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar campos de respuesta
        expected_fields = [
            'yolo_segmentation', 'regression_models', 'device', 'models_info', 'status'
        ]
        
        for field in expected_fields:
            self.assertIn(field, response.data)
        
        # Verificar que todos los modelos están cargados
        regression_models = response.data['regression_models']
        for target in ['alto', 'ancho', 'grosor', 'peso']:
            self.assertEqual(regression_models[target], 'loaded')
    
    @patch('api.views.get_predictor')
    def test_models_status_not_loaded(self, mock_get_predictor):
        """Test cuando los modelos no están cargados."""
        # Mock predictor sin modelos cargados
        mock_predictor = Mock()
        mock_predictor.get_model_info.return_value = {
            'status': 'not_loaded'
        }
        mock_get_predictor.return_value = mock_predictor
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'not_loaded')
        
        # Verificar que todos los modelos están marcados como no cargados
        regression_models = response.data['regression_models']
        for target in ['alto', 'ancho', 'grosor', 'peso']:
            self.assertEqual(regression_models[target], 'not_loaded')
    
    @patch('api.views.get_predictor')
    def test_models_status_error(self, mock_get_predictor):
        """Test con error al obtener estado de modelos."""
        mock_get_predictor.side_effect = Exception("Error de predictor")
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', response.data)


class TestLoadModelsAPI(TestCase):
    """Tests para el endpoint de carga de modelos."""
    
    def setUp(self):
        """Configuración antes de cada test."""
        self.client = APIClient()
        self.url = reverse('load-models')
    
    @patch('api.views.load_artifacts')
    def test_load_models_success(self, mock_load_artifacts):
        """Test de carga exitosa de modelos."""
        mock_load_artifacts.return_value = True
        
        response = self.client.post(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('message', response.data)
    
    @patch('api.views.load_artifacts')
    def test_load_models_failure(self, mock_load_artifacts):
        """Test de fallo en carga de modelos."""
        mock_load_artifacts.return_value = False
        
        response = self.client.post(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data['status'], 'error')
        self.assertIn('error', response.data)
    
    @patch('api.views.load_artifacts')
    def test_load_models_exception(self, mock_load_artifacts):
        """Test con excepción en carga de modelos."""
        mock_load_artifacts.side_effect = Exception("Error de carga")
        
        response = self.client.post(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data['status'], 'error')
        self.assertIn('error', response.data)


class TestDatasetValidationAPI(TestCase):
    """Tests para el endpoint de validación de dataset."""
    
    def setUp(self):
        """Configuración antes de cada test."""
        self.client = APIClient()
        self.url = reverse('dataset-validation')
    
    @patch('api.views.CacaoDatasetLoader')
    def test_dataset_validation_success(self, mock_loader_class):
        """Test de validación exitosa del dataset."""
        # Mock loader con datos válidos
        mock_loader = Mock()
        mock_loader.get_dataset_stats.return_value = {
            'total_records': 100,
            'valid_records': 95,
            'missing_images': 5,
            'missing_ids': [1, 2, 3, 4, 5],
            'dimensions_stats': {}
        }
        mock_loader_class.return_value = mock_loader
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar campos de respuesta
        expected_fields = ['valid', 'stats', 'status']
        for field in expected_fields:
            self.assertIn(field, response.data)
        
        self.assertEqual(response.data['status'], 'success')
        self.assertFalse(response.data['valid'])  # Hay imágenes faltantes
    
    @patch('api.views.CacaoDatasetLoader')
    def test_dataset_validation_error(self, mock_loader_class):
        """Test con error en validación del dataset."""
        mock_loader_class.side_effect = Exception("Error de dataset")
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data['status'], 'error')
        self.assertIn('error', response.data)


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
        response = self.client.get(reverse('models-status'))
        
        # Verificar que CORS está configurado
        self.assertIn('Access-Control-Allow-Origin', response)
    
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
