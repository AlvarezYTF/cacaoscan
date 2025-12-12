"""
Tests for image statistics views.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from rest_framework.test import APIRequestFactory
from rest_framework import status
from django.contrib.auth.models import User

from images_app.views.image.user.stats_views import ImagesStatsView
from images_app.views.image.admin.stats_views import AdminDatasetStatsView


@pytest.fixture
def request_factory():
    """Create API request factory."""
    return APIRequestFactory()


@pytest.fixture
def user(db):
    """Create a test user with unique username and email."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    return User.objects.create_user(
        username=f'testuser_{unique_id}',
        email=f'test_{unique_id}@example.com',
        password='testpass123'
    )


@pytest.fixture
def admin_user(db):
    """Create an admin user with unique username and email."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    return User.objects.create_superuser(
        username=f'admin_{unique_id}',
        email=f'admin_{unique_id}@example.com',
        password='adminpass123'
    )


@pytest.mark.django_db
class TestImagesStatsView:
    """Tests for ImagesStatsView."""
    
    def test_get_stats_success(self, request_factory, user):
        """Test successful retrieval of image statistics."""
        view = ImagesStatsView()
        request = request_factory.get('/api/images/stats/')
        request.user = user
        
        with patch.object(view, 'get_user_images_queryset') as mock_queryset_method:
            mock_qs = Mock()
            mock_queryset_method.return_value = mock_qs
            
            # Mock count() method properly - it should return a value directly
            mock_qs.count = Mock(return_value=10)
            
            # Mock filter() to return a new queryset that also has count()
            # Each filter call should return a new queryset with count()
            def create_filtered_mock(count_value):
                filtered = Mock()
                filtered.count = Mock(return_value=count_value)
                # Chain filter calls
                filtered.filter = Mock(return_value=filtered)
                return filtered
            
            # Main queryset filter returns a filtered queryset
            # The filter is called multiple times with different arguments
            # We need to handle all filter calls properly
            filtered_mock = create_filtered_mock(8)
            mock_qs.filter = Mock(return_value=filtered_mock)
            
            with patch('images_app.views.image.user.stats_views.CacaoPrediction') as mock_prediction:
                mock_pred_qs = Mock()
                mock_prediction.objects.filter.return_value = mock_pred_qs
                mock_pred_qs.aggregate.return_value = {
                    'avg_confidence': 0.85,
                    'avg_time': 150.0,
                    'avg_alto': 25.5,
                    'avg_ancho': 20.3,
                    'avg_grosor': 15.2,
                    'avg_peso': 8.5
                }
                # Mock values().annotate().order_by() chain
                mock_values_result = Mock()
                mock_annotate_result = Mock()
                mock_order_by_result = []
                mock_annotate_result.order_by.return_value = mock_order_by_result
                mock_values_result.annotate.return_value = mock_annotate_result
                mock_pred_qs.values.return_value = mock_values_result
                
                # Mock values().annotate() for region_stats and finca_stats
                mock_qs.values = Mock(return_value=mock_values_result)
                
                response = view.get(request)
                
                assert response.status_code == status.HTTP_200_OK
                assert 'total_images' in response.data
                assert response.data['total_images'] == 10
    
    def test_get_stats_error(self, request_factory, user):
        """Test error handling in stats retrieval."""
        view = ImagesStatsView()
        request = request_factory.get('/api/images/stats/')
        request.user = user
        
        with patch.object(view, 'get_user_images_queryset', side_effect=Exception("Database error")):
            response = view.get(request)
            
            assert response.status_code == status.HTTP_200_OK
            assert response.data['total_images'] == 0


@pytest.mark.django_db
class TestAdminDatasetStatsView:
    """Tests for AdminDatasetStatsView."""
    
    def test_get_stats_admin_success(self, request_factory, admin_user):
        """Test successful retrieval of admin dataset statistics."""
        view = AdminDatasetStatsView()
        request = request_factory.get('/api/admin/dataset/stats/')
        request.user = admin_user
        
        with patch.object(view, 'is_admin_user', return_value=True):
            with patch('images_app.views.image.admin.stats_views.CacaoImage') as mock_image:
                mock_image.objects.count.return_value = 100
                mock_image.objects.filter.return_value.count.return_value = 80
                mock_image.objects.values.return_value.annotate.return_value.order_by.return_value.__getitem__.return_value = []
                mock_image.objects.values.return_value.distinct.return_value.count.return_value = 5
                
                with patch('images_app.views.image.admin.stats_views.CacaoPrediction') as mock_prediction:
                    mock_prediction.objects.aggregate.return_value = {
                        'avg_alto': 25.5,
                        'avg_ancho': 20.3,
                        'avg_grosor': 15.2,
                        'avg_peso': 8.5,
                        'avg_processing_time': 150.0
                    }
                    mock_prediction.objects.all.return_value.aggregate.return_value = {
                        'avg': 0.85,
                        'min': 0.70,
                        'max': 0.95
                    }
                    mock_prediction.objects.values.return_value.annotate.return_value.order_by.return_value = []
                    
                    with patch.object(view, '_get_top_users', return_value=[]):
                        response = view.get(request)
                        
                        assert response.status_code == status.HTTP_200_OK
                        assert 'dataset_overview' in response.data
                        assert 'generated_at' in response.data
    
    def test_get_stats_non_admin(self, request_factory, user):
        """Test that non-admin users cannot access admin stats."""
        view = AdminDatasetStatsView()
        request = request_factory.get('/api/admin/dataset/stats/')
        request.user = user
        
        with patch.object(view, 'is_admin_user', return_value=False):
            response = view.get(request)
            
            assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_stats_error(self, request_factory, admin_user):
        """Test error handling in admin stats retrieval."""
        view = AdminDatasetStatsView()
        request = request_factory.get('/api/admin/dataset/stats/')
        request.user = admin_user
        
        with patch.object(view, 'is_admin_user', return_value=True):
            with patch('images_app.views.image.admin.stats_views.CacaoImage', side_effect=Exception("Database error")):
                response = view.get(request)
                
                assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
                assert 'error' in response.data
    
    def test_get_basic_dataset_stats(self, admin_user):
        """Test _get_basic_dataset_stats method."""
        view = AdminDatasetStatsView()
        
        with patch('images_app.views.image.admin.stats_views.CacaoImage') as mock_image:
            mock_image.objects.count.return_value = 100
            mock_image.objects.filter.return_value.count.side_effect = [80, 20]
            
            stats = view._get_basic_dataset_stats()
            
            assert stats['total_images'] == 100
            assert stats['processed_images'] == 80
            assert stats['pending_images'] == 20
    
    def test_get_temporal_stats(self, admin_user):
        """Test _get_temporal_stats method."""
        view = AdminDatasetStatsView()
        
        with patch('images_app.views.image.admin.stats_views.CacaoImage') as mock_image:
            mock_image.objects.filter.return_value.count.side_effect = [5, 20, 50]
            
            stats = view._get_temporal_stats()
            
            assert 'last_24h' in stats
            assert 'last_7d' in stats
            assert 'last_30d' in stats
    
    def test_get_confidence_stats(self, admin_user):
        """Test _get_confidence_stats method."""
        view = AdminDatasetStatsView()
        
        with patch('images_app.views.image.admin.stats_views.CacaoPrediction') as mock_prediction:
            mock_prediction.objects.all.return_value.aggregate.return_value = {
                'avg': 0.85,
                'min': 0.70,
                'max': 0.95
            }
            
            stats = view._get_confidence_stats()
            
            assert 'avg_confidence' in stats
            assert 'min_confidence' in stats
            assert 'max_confidence' in stats
    
    def test_get_model_stats(self, admin_user):
        """Test _get_model_stats method."""
        view = AdminDatasetStatsView()
        
        with patch('images_app.views.image.admin.stats_views.CacaoPrediction') as mock_prediction:
            mock_prediction.objects.values.return_value.annotate.return_value.order_by.return_value = [
                {'model_version': 'v1.0', 'count': 50, 'avg_confidence': 0.85}
            ]
            
            stats = view._get_model_stats()
            
            assert isinstance(stats, list)
    
    def test_get_device_stats(self, admin_user):
        """Test _get_device_stats method."""
        view = AdminDatasetStatsView()
        
        with patch('images_app.views.image.admin.stats_views.CacaoPrediction') as mock_prediction:
            mock_prediction.objects.values.return_value.annotate.return_value.order_by.return_value = [
                {'device_used': 'mobile', 'count': 30, 'avg_processing_time': 150.0}
            ]
            
            stats = view._get_device_stats()
            
            assert isinstance(stats, list)
    
    def test_get_top_users(self, admin_user):
        """Test _get_top_users method."""
        view = AdminDatasetStatsView()
        
        user1 = User.objects.create_user(username='user1', email='user1@test.com', password='pass')
        user2 = User.objects.create_user(username='user2', email='user2@test.com', password='pass')
        
        with patch('images_app.views.image.admin.stats_views.User') as mock_user:
            mock_user.objects.annotate.return_value.order_by.return_value.__getitem__.return_value = [
                Mock(id=user1.id, username='user1', email='user1@test.com', image_count=10, processed_count=8),
                Mock(id=user2.id, username='user2', email='user2@test.com', image_count=5, processed_count=4)
            ]
            
            users = view._get_top_users()
            
            assert isinstance(users, list)
    
    def test_get_file_stats(self, admin_user):
        """Test _get_file_stats method."""
        view = AdminDatasetStatsView()
        
        with patch('images_app.views.image.admin.stats_views.CacaoImage') as mock_image:
            mock_image.objects.aggregate.return_value = {
                'total_size': 1024 * 1024 * 100,  # 100 MB
                'avg_size': 1024 * 1024  # 1 MB
            }
            
            stats = view._get_file_stats()
            
            assert 'total_size' in stats
            assert 'avg_size' in stats
    
    def test_get_metadata_completeness(self, admin_user):
        """Test _get_metadata_completeness method."""
        view = AdminDatasetStatsView()
        
        with patch('images_app.views.image.admin.stats_views.CacaoImage') as mock_image:
            mock_image.objects.filter.return_value.count.return_value = 75
            
            count = view._get_metadata_completeness()
            
            assert isinstance(count, int)


