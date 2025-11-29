"""
Tests para endpoints de imágenes de CacaoScan.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io

from api.models import CacaoImage, CacaoPrediction
from api.tests.test_constants import (
    TEST_USER_PASSWORD,
    TEST_ADMIN_PASSWORD,
    TEST_OTHER_USER_PASSWORD,
    TEST_USER_USERNAME,
    TEST_USER_EMAIL,
    TEST_ADMIN_USERNAME,
    TEST_ADMIN_EMAIL,
    TEST_OTHER_USER_USERNAME,
    TEST_OTHER_USER_EMAIL,
)


class ImagesEndpointsTestCase(APITestCase):
    """Tests para endpoints de imágenes."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        # Crear usuarios
        # Using test constants to avoid hard-coded passwords (SonarQube S2068)
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD  # NOSONAR(S2068)
        )
        
        self.admin_user = User.objects.create_superuser(
            username=TEST_ADMIN_USERNAME,
            email=TEST_ADMIN_EMAIL,
            password=TEST_ADMIN_PASSWORD  # NOSONAR(S2068)
        )
        
        # Crear imagen de prueba
        self.test_image = self._create_test_image()
        
        # Crear CacaoImage de prueba
        self.cacao_image = CacaoImage.objects.create(
            user=self.user,
            image=self.test_image,
            file_name='test_image.jpg',
            file_size=1024,
            file_type='image/jpeg',
            processed=True,
            finca='Finca Test',
            region='Región Test'
        )
        
        # Crear predicción de prueba
        self.cacao_prediction = CacaoPrediction.objects.create(
            image=self.cacao_image,
            alto_mm=15.5,
            ancho_mm=12.3,
            grosor_mm=8.7,
            peso_g=1.2,
            confidence_alto=0.95,
            confidence_ancho=0.92,
            confidence_grosor=0.88,
            confidence_peso=0.90,
            processing_time_ms=1500,
            model_version='v1.0',
            device_used='cpu'
        )
    
    def _create_test_image(self):
        """Crear imagen de prueba."""
        img = Image.new('RGB', (100, 100), color='red')
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG')
        img_io.seek(0)
        
        return SimpleUploadedFile(
            'test_image.jpg',
            img_io.getvalue(),
            content_type='image/jpeg'
        )
    
    def test_images_list_authenticated(self):
        """Test lista de imágenes para usuario autenticado."""
        self.client.force_authenticate(user=self.user)
        url = reverse('images-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 1)
    
    def test_images_list_unauthenticated(self):
        """Test lista de imágenes para usuario no autenticado."""
        url = reverse('images-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_images_list_with_filters(self):
        """Test lista de imágenes con filtros."""
        self.client.force_authenticate(user=self.user)
        url = reverse('images-list')
        
        # Filtrar por región
        response = self.client.get(url, {'region': 'Región Test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        
        # Filtrar por finca
        response = self.client.get(url, {'finca': 'Finca Test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        
        # Filtrar por procesado
        response = self.client.get(url, {'processed': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
    
    def test_images_list_pagination(self):
        """Test paginación en lista de imágenes."""
        self.client.force_authenticate(user=self.user)
        url = reverse('images-list')
        
        response = self.client.get(url, {'page': 1, 'page_size': 10})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('page', response.data)
        self.assertIn('total_pages', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
    
    def test_image_detail_owner_access(self):
        """Test acceso a detalles de imagen por propietario."""
        self.client.force_authenticate(user=self.user)
        url = reverse('image-detail', kwargs={'image_id': self.cacao_image.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.cacao_image.id)
        self.assertIn('prediction', response.data)
    
    def test_image_detail_admin_access(self):
        """Test acceso a detalles de imagen por admin."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('image-detail', kwargs={'image_id': self.cacao_image.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.cacao_image.id)
    
    def test_image_detail_not_found(self):
        """Test detalles de imagen no encontrada."""
        self.client.force_authenticate(user=self.user)
        url = reverse('image-detail', kwargs={'image_id': 99999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_image_detail_unauthorized_access(self):
        """Test acceso no autorizado a detalles de imagen."""
        # Crear otro usuario
        # Using test constant to avoid hard-coded password (SonarQube S2068)
        other_user = User.objects.create_user(
            username=TEST_OTHER_USER_USERNAME,
            email=TEST_OTHER_USER_EMAIL,
            password=TEST_OTHER_USER_PASSWORD  # NOSONAR(S2068)
        )
        
        self.client.force_authenticate(user=other_user)
        url = reverse('image-detail', kwargs={'image_id': self.cacao_image.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_images_stats_authenticated(self):
        """Test estadísticas de imágenes para usuario autenticado."""
        self.client.force_authenticate(user=self.user)
        url = reverse('images-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_images', response.data)
        self.assertIn('processed_images', response.data)
        self.assertIn('average_confidence', response.data)
        self.assertIn('region_stats', response.data)
        self.assertIn('top_fincas', response.data)
        self.assertIn('average_dimensions', response.data)
    
    def test_images_stats_unauthenticated(self):
        """Test estadísticas de imágenes para usuario no autenticado."""
        url = reverse('images-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_images_stats_data_accuracy(self):
        """Test precisión de datos en estadísticas."""
        self.client.force_authenticate(user=self.user)
        url = reverse('images-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.data['total_images'], 1)
        self.assertEqual(response.data['processed_images'], 1)
        self.assertEqual(response.data['unprocessed_images'], 0)
        self.assertGreater(response.data['average_confidence'], 0)


