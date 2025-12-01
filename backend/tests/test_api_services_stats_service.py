"""
Unit tests for stats service module (stats_service.py).
Tests statistics generation functionality.
"""
import pytest
from unittest.mock import Mock, patch
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from api.services.stats.stats_service import StatsService


@pytest.fixture
def stats_service():
    """Create a StatsService instance for testing."""
    return StatsService()


@pytest.fixture
def django_users(db):
    """Create multiple Django users for testing."""
    users = []
    for i in range(5):
        user = User.objects.create_user(
            username=f'user{i}',
            email=f'user{i}@example.com',
            password='testpass123',
            is_active=True
        )
        users.append(user)
    
    # Create one staff user
    staff_user = User.objects.create_user(
        username='staff',
        email='staff@example.com',
        password='testpass123',
        is_staff=True,
        is_active=True
    )
    users.append(staff_user)
    
    # Create one superuser
    superuser = User.objects.create_user(
        username='admin',
        email='admin@example.com',
        password='testpass123',
        is_superuser=True,
        is_staff=True,
        is_active=True
    )
    users.append(superuser)
    
    return users


class TestStatsService:
    """Tests for StatsService class."""
    
    def test_service_initialization(self, stats_service):
        """Test service initialization."""
        assert stats_service is not None
        assert hasattr(stats_service, 'CacaoImage')
        assert hasattr(stats_service, 'CacaoPrediction')
        assert hasattr(stats_service, 'Finca')
    
    def test_get_user_stats_success(self, stats_service, django_users):
        """Test getting user statistics successfully."""
        stats = stats_service.get_user_stats()
        
        assert 'total' in stats
        assert 'active' in stats
        assert 'staff' in stats
        assert 'superusers' in stats
        assert stats['total'] == 7  # 5 regular + 1 staff + 1 superuser
        assert stats['active'] == 7
        assert stats['staff'] == 2  # 1 staff + 1 superuser
        assert stats['superusers'] == 1
        assert 'analysts' in stats
        assert 'farmers' in stats
        assert 'verified' in stats
        assert 'this_week' in stats
        assert 'this_month' in stats
    
    def test_get_user_stats_with_groups(self, stats_service, db):
        """Test getting user stats with groups."""
        from django.contrib.auth.models import Group
        
        # Create analyst group
        analyst_group, _ = Group.objects.get_or_create(name='analyst')
        
        # Create users
        regular_user = User.objects.create_user(
            username='farmer',
            email='farmer@example.com',
            password='testpass123'
        )
        
        analyst_user = User.objects.create_user(
            username='analyst',
            email='analyst@example.com',
            password='testpass123'
        )
        analyst_user.groups.add(analyst_group)
        
        stats = stats_service.get_user_stats()
        
        assert stats['analysts'] >= 1
        assert stats['farmers'] >= 1
    
    def test_get_user_stats_recent_users(self, stats_service, db):
        """Test getting user stats with recent users."""
        # Create user from this week
        recent_user = User.objects.create_user(
            username='recent',
            email='recent@example.com',
            password='testpass123',
            date_joined=timezone.now() - timedelta(days=3)
        )
        
        stats = stats_service.get_user_stats()
        
        assert stats['this_week'] >= 1
        assert stats['this_month'] >= 1
    
    @patch('api.services.stats.stats_service.get_models_safely')
    def test_get_image_stats_success(self, mock_get_models, stats_service):
        """Test getting image statistics successfully."""
        mock_image_model = Mock()
        mock_queryset = Mock()
        mock_queryset.count.return_value = 100
        mock_queryset.filter.return_value.count.return_value = 80
        mock_image_model.objects.count.return_value = 100
        mock_image_model.objects.filter.return_value.count.return_value = 80
        
        # Mock date filtering
        def filter_side_effect(*args, **kwargs):
            if 'created_at__date__gte' in kwargs:
                return mock_queryset
            return mock_queryset
        
        mock_image_model.objects.filter.side_effect = filter_side_effect
        mock_get_models.return_value = {
            'CacaoImage': mock_image_model,
            'CacaoPrediction': None,
            'Finca': None
        }
        
        stats_service.CacaoImage = mock_image_model
        
        stats = stats_service.get_image_stats()
        
        assert 'total' in stats
        assert 'processed' in stats
        assert 'unprocessed' in stats
        assert 'this_week' in stats
        assert 'this_month' in stats
        assert 'processing_rate' in stats
        assert stats['total'] == 100
        assert stats['processed'] == 80
        assert stats['unprocessed'] == 20
    
    def test_get_image_stats_no_model(self, stats_service):
        """Test getting image stats when model is not available."""
        stats_service.CacaoImage = None
        
        stats = stats_service.get_image_stats()
        
        assert stats['total'] == 0
        assert stats['processed'] == 0
        assert stats['unprocessed'] == 0
        assert stats['processing_rate'] == 0
    
    @patch('api.services.stats.stats_service.get_models_safely')
    def test_get_prediction_stats_success(self, mock_get_models, stats_service):
        """Test getting prediction statistics successfully."""
        mock_prediction_model = Mock()
        mock_queryset = Mock()
        mock_queryset.count.return_value = 50
        
        # Mock aggregate
        mock_queryset.aggregate.return_value = {
            'avg_alto': 25.5,
            'avg_ancho': 15.3,
            'avg_grosor': 8.2,
            'avg_peso': 1.5,
            'avg_processing_time': 100.0,
            'avg_confidence': 0.85
        }
        
        # Mock annotation for quality distribution
        mock_annotated_queryset = Mock()
        mock_annotated_queryset.filter.return_value.count.return_value = 10
        mock_queryset.annotate.return_value = mock_annotated_queryset
        
        mock_prediction_model.objects.count.return_value = 50
        mock_prediction_model.objects.aggregate.return_value = {
            'avg_alto': 25.5,
            'avg_ancho': 15.3,
            'avg_grosor': 8.2,
            'avg_peso': 1.5,
            'avg_processing_time': 100.0,
            'avg_confidence': 0.85
        }
        mock_prediction_model.objects.annotate.return_value = mock_annotated_queryset
        
        mock_get_models.return_value = {
            'CacaoImage': None,
            'CacaoPrediction': mock_prediction_model,
            'Finca': None
        }
        
        stats_service.CacaoPrediction = mock_prediction_model
        
        stats = stats_service.get_prediction_stats()
        
        assert 'total' in stats
        assert 'average_dimensions' in stats
        assert 'average_confidence' in stats
        assert 'average_processing_time_ms' in stats
        assert 'quality_distribution' in stats
        assert stats['total'] == 50
        assert stats['average_confidence'] == 0.85
    
    def test_get_prediction_stats_no_model(self, stats_service):
        """Test getting prediction stats when model is not available."""
        stats_service.CacaoPrediction = None
        
        stats = stats_service.get_prediction_stats()
        
        assert stats['total'] == 0
        assert stats['average_confidence'] == 0
        assert 'average_dimensions' in stats
    
    @patch('api.services.stats.stats_service.get_models_safely')
    def test_get_activity_by_day_success(self, mock_get_models, stats_service):
        """Test getting activity by day statistics."""
        mock_image_model = Mock()
        mock_prediction_model = Mock()
        
        # Mock queryset for images
        mock_image_queryset = Mock()
        mock_image_queryset.filter.return_value.annotate.return_value.values.return_value.annotate.return_value.values_list.return_value = [
            (timezone.now().date() - timedelta(days=1), 5),
            (timezone.now().date(), 10)
        ]
        mock_image_model.objects.filter.return_value.annotate.return_value.values.return_value.annotate.return_value.values_list.return_value = [
            (timezone.now().date() - timedelta(days=1), 5),
            (timezone.now().date(), 10)
        ]
        
        # Mock queryset for predictions
        mock_prediction_queryset = Mock()
        mock_prediction_queryset.filter.return_value.annotate.return_value.values.return_value.annotate.return_value.values_list.return_value = [
            (timezone.now().date(), 3)
        ]
        mock_prediction_model.objects.filter.return_value.annotate.return_value.values.return_value.annotate.return_value.values_list.return_value = [
            (timezone.now().date(), 3)
        ]
        
        mock_get_models.return_value = {
            'CacaoImage': mock_image_model,
            'CacaoPrediction': mock_prediction_model,
            'Finca': None
        }
        
        stats_service.CacaoImage = mock_image_model
        stats_service.CacaoPrediction = mock_prediction_model
        
        stats = stats_service.get_activity_by_day(max_days=7)
        
        assert 'labels' in stats
        assert 'data' in stats
        assert isinstance(stats['labels'], list)
        assert isinstance(stats['data'], list)
        assert len(stats['labels']) == len(stats['data'])
    
    def test_get_activity_by_day_with_users(self, stats_service, db):
        """Test getting activity by day with real users."""
        # Create users at different dates
        User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123',
            date_joined=timezone.now() - timedelta(days=2)
        )
        
        User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123',
            date_joined=timezone.now()
        )
        
        stats = stats_service.get_activity_by_day(max_days=7)
        
        assert 'labels' in stats
        assert 'data' in stats
        assert len(stats['data']) <= 7
    
    @patch('api.services.stats.stats_service.get_models_safely')
    def test_get_finca_stats_success(self, mock_get_models, stats_service):
        """Test getting finca statistics successfully."""
        mock_finca_model = Mock()
        mock_queryset = Mock()
        mock_queryset.count.return_value = 20
        mock_queryset.filter.return_value.count.return_value = 5
        
        mock_finca_model.objects.count.return_value = 20
        mock_finca_model.objects.filter.return_value.count.return_value = 5
        
        mock_get_models.return_value = {
            'CacaoImage': None,
            'CacaoPrediction': None,
            'Finca': mock_finca_model
        }
        
        stats_service.Finca = mock_finca_model
        
        stats = stats_service.get_finca_stats()
        
        assert 'total' in stats
        assert 'this_week' in stats
        assert 'this_month' in stats
        assert stats['total'] == 20
    
    def test_get_finca_stats_no_model(self, stats_service):
        """Test getting finca stats when model is not available."""
        stats_service.Finca = None
        
        stats = stats_service.get_finca_stats()
        
        assert stats['total'] == 0
        assert stats['this_week'] == 0
        assert stats['this_month'] == 0
    
    @patch('api.services.stats.stats_service.get_models_safely')
    def test_get_top_regions_success(self, mock_get_models, stats_service):
        """Test getting top regions successfully."""
        mock_image_model = Mock()
        mock_queryset = Mock()
        mock_queryset.values.return_value.annotate.return_value.order_by.return_value = [
            {'region': 'Region1', 'count': 10, 'processed_count': 8},
            {'region': 'Region2', 'count': 5, 'processed_count': 4}
        ]
        
        mock_image_model.objects.values.return_value.annotate.return_value.order_by.return_value = [
            {'region': 'Region1', 'count': 10, 'processed_count': 8},
            {'region': 'Region2', 'count': 5, 'processed_count': 4}
        ]
        
        mock_get_models.return_value = {
            'CacaoImage': mock_image_model,
            'CacaoPrediction': None,
            'Finca': None
        }
        
        stats_service.CacaoImage = mock_image_model
        
        regions = stats_service.get_top_regions(limit=10)
        
        assert isinstance(regions, list)
        assert len(regions) == 2
        assert regions[0]['region'] == 'Region1'
        assert regions[0]['count'] == 10
    
    def test_get_top_regions_no_model(self, stats_service):
        """Test getting top regions when model is not available."""
        stats_service.CacaoImage = None
        
        regions = stats_service.get_top_regions()
        
        assert isinstance(regions, list)
        assert len(regions) == 0
    
    @patch('api.services.stats.stats_service.get_models_safely')
    def test_get_top_fincas_success(self, mock_get_models, stats_service):
        """Test getting top fincas successfully."""
        mock_image_model = Mock()
        mock_queryset = Mock()
        mock_queryset.values.return_value.annotate.return_value.order_by.return_value = [
            {'finca': 1, 'count': 15, 'processed_count': 12},
            {'finca': 2, 'count': 8, 'processed_count': 6}
        ]
        
        mock_image_model.objects.values.return_value.annotate.return_value.order_by.return_value = [
            {'finca': 1, 'count': 15, 'processed_count': 12},
            {'finca': 2, 'count': 8, 'processed_count': 6}
        ]
        
        mock_get_models.return_value = {
            'CacaoImage': mock_image_model,
            'CacaoPrediction': None,
            'Finca': None
        }
        
        stats_service.CacaoImage = mock_image_model
        
        fincas = stats_service.get_top_fincas(limit=10)
        
        assert isinstance(fincas, list)
        assert len(fincas) == 2
        assert fincas[0]['finca'] == 1
        assert fincas[0]['count'] == 15
    
    def test_get_top_fincas_no_model(self, stats_service):
        """Test getting top fincas when model is not available."""
        stats_service.CacaoImage = None
        
        fincas = stats_service.get_top_fincas()
        
        assert isinstance(fincas, list)
        assert len(fincas) == 0
    
    @patch.object(StatsService, 'get_user_stats')
    @patch.object(StatsService, 'get_image_stats')
    @patch.object(StatsService, 'get_prediction_stats')
    @patch.object(StatsService, 'get_activity_by_day')
    @patch.object(StatsService, 'get_finca_stats')
    @patch.object(StatsService, 'get_top_regions')
    @patch.object(StatsService, 'get_top_fincas')
    def test_get_all_stats_success(self, mock_top_fincas, mock_top_regions, mock_finca,
                                    mock_activity, mock_prediction, mock_image, mock_user,
                                    stats_service):
        """Test getting all statistics successfully."""
        mock_user.return_value = {'total': 10, 'active': 8}
        mock_image.return_value = {'total': 100, 'processed': 80}
        mock_prediction.return_value = {
            'total': 50,
            'average_confidence': 0.85,
            'quality_distribution': {
                'excelente': 20,
                'buena': 15,
                'regular': 10,
                'baja': 5
            }
        }
        mock_activity.return_value = {'labels': ['Day1'], 'data': [5]}
        mock_finca.return_value = {'total': 20}
        mock_top_regions.return_value = [{'region': 'Region1', 'count': 10}]
        mock_top_fincas.return_value = [{'finca': 1, 'count': 15}]
        
        stats = stats_service.get_all_stats()
        
        assert 'users' in stats
        assert 'images' in stats
        assert 'predictions' in stats
        assert 'fincas' in stats
        assert 'top_regions' in stats
        assert 'top_fincas' in stats
        assert 'activity_by_day' in stats
        assert 'quality_distribution' in stats
        assert 'generated_at' in stats
    
    def test_get_all_stats_exception(self, stats_service):
        """Test getting all stats when exception occurs."""
        with patch.object(stats_service, 'get_user_stats', side_effect=Exception("Error")):
            stats = stats_service.get_all_stats()
            
            # Should return empty stats
            assert 'users' in stats
            assert stats['users']['total'] == 0
    
    def test_get_empty_stats(self, stats_service):
        """Test getting empty statistics structure."""
        empty_stats = stats_service.get_empty_stats()
        
        assert 'users' in empty_stats
        assert 'images' in empty_stats
        assert 'predictions' in empty_stats
        assert empty_stats['users']['total'] == 0
        assert empty_stats['images']['total'] == 0
        assert empty_stats['predictions']['total'] == 0
        assert 'generated_at' in empty_stats

