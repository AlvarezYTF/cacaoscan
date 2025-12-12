"""
Tests for batch upload views.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from images_app.views.image.batch.batch_upload_views import BatchAnalysisView


@pytest.mark.django_db
class TestBatchAnalysisView:
    """Tests for BatchAnalysisView."""
    
    @pytest.fixture
    def api_client(self):
        """Create API client."""
        return APIClient()
    
    @pytest.fixture
    def admin_user(self, db):
        """Create admin user with unique username and email."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        return User.objects.create_user(
            username=f'admin_{unique_id}',
            email=f'admin_{unique_id}@example.com',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
    
    @pytest.fixture
    def image_file(self):
        """Create test image file."""
        from PIL import Image
        import io
        
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        return SimpleUploadedFile(
            "test_image.jpg",
            img_bytes.read(),
            content_type="image/jpeg"
        )
    
    @patch('images_app.views.image.batch.batch_upload_views.process_batch_analysis_task')
    def test_batch_analysis_post_success(self, mock_task, api_client, admin_user, image_file):
        """Test successful batch analysis POST."""
        mock_task.delay.return_value = Mock(id='task-123')
        
        # Mock the methods that create finca and lote
        view = BatchAnalysisView()
        with patch.object(view, '_get_or_create_finca') as mock_get_finca:
            with patch.object(view, '_get_or_create_lote') as mock_get_lote:
                with patch.object(view, '_save_images_temporarily') as mock_save_images:
                    from fincas_app.models import Finca, Lote
                    mock_finca = Mock(spec=Finca)
                    mock_finca.id = 1
                    mock_finca.nombre = 'Test Farm'
                    mock_finca.agricultor_id = admin_user.id
                    mock_get_finca.return_value = mock_finca
                    
                    mock_lote = Mock(spec=Lote)
                    mock_lote.id = 1
                    mock_get_lote.return_value = mock_lote
                    
                    mock_save_images.return_value = [{'file_name': 'test.jpg', 'temp_path': '/tmp/test.jpg'}]
                    
                    with patch.object(view, 'is_admin_user', return_value=True):
                        # Create a mock request with all needed attributes
                        mock_request = MagicMock()
                        mock_request.data = {
                            'name': 'Test Lote',
                            'farm': 'Test Farm',
                            'genetics': 'Criollo',
                            'collectionDate': '2024-01-01'
                        }
                        mock_request.FILES = MagicMock()
                        mock_request.FILES.getlist = Mock(return_value=[image_file])
                        mock_request.user = admin_user
                        
                        response = view.post(mock_request)
                        
                        assert response.status_code in [status.HTTP_202_ACCEPTED, status.HTTP_200_OK]
    
    def test_batch_analysis_post_unauthenticated(self, api_client, image_file):
        """Test batch analysis POST without authentication."""
        from rest_framework.test import APIRequestFactory
        from django.contrib.auth.models import AnonymousUser
        
        view = BatchAnalysisView()
        api_factory = APIRequestFactory()
        
        # Create request without authentication - DRF will handle permission check
        request = api_factory.post('/api/batch/analysis/', {
            'name': 'Test Lote',
            'farm': 'Test Farm',
            'genetics': 'Criollo',
            'collectionDate': '2024-01-01'
        }, format='multipart')
        
        # Use dispatch to properly handle permission checks (DRF's way)
        # This will check permissions BEFORE calling post()
        response = view.dispatch(request, 'POST')
        
        # Should return 401 for unauthenticated requests due to IsAuthenticated permission
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_batch_analysis_post_missing_fields(self, api_client, admin_user):
        """Test batch analysis POST with missing required fields."""
        view = BatchAnalysisView()
        
        # Create a mock request with missing fields
        mock_request = MagicMock()
        mock_request.data = {'name': 'Test Lote'}
        mock_request.FILES = MagicMock()
        mock_request.FILES.getlist = Mock(return_value=[])
        mock_request.user = admin_user
        
        with patch.object(view, 'is_admin_user', return_value=True):
            response = view.post(mock_request)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
