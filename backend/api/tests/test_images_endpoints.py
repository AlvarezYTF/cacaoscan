"""
Tests para endpoints de imÃ¡genes de CacaoScan.
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


class ImagesEndpointsTestCase(APITestCase):
    """Tests para endpoints de imÃ¡genes."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        # Crear usuarios
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
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
            region='RegiÃ³n Test'
        )
        
        # Crear predicciÃ³n de prueba
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
        """Test lista de imÃ¡genes para usuario autenticado."""
        self.client.force_authenticate(user=self.user)
        url = reverse('images-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 1)
    
    def test_images_list_unauthenticated(self):
        """Test lista de imÃ¡genes para usuario no autenticado."""
        url = reverse('images-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_images_list_with_filters(self):
        """Test lista de imÃ¡genes con filtros."""
        self.client.force_authenticate(user=self.user)
        url = reverse('images-list')
        
        # Filtrar por regiÃ³n
        response = self.client.get(url, {'region': 'RegiÃ³n Test'})
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
        """Test paginaciÃ³n en lista de imÃ¡genes."""
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
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        self.client.force_authenticate(user=other_user)
        url = reverse('image-detail', kwargs={'image_id': self.cacao_image.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_images_stats_authenticated(self):
        """Test estadÃ­sticas de imÃ¡genes para usuario autenticado."""
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
        """Test estadÃ­sticas de imÃ¡genes para usuario no autenticado."""
        url = reverse('images-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_images_stats_data_accuracy(self):
        """Test precisiÃ³n de datos en estadÃ­sticas."""
        self.client.force_authenticate(user=self.user)
        url = reverse('images-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.data['total_images'], 1)
        self.assertEqual(response.data['processed_images'], 1)
        self.assertEqual(response.data['unprocessed_images'], 0)
        self.assertGreater(response.data['average_confidence'], 0)


