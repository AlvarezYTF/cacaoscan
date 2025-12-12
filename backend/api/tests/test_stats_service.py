"""
Tests for stats service.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User, Group

from api.services.stats.stats_service import StatsService


@pytest.fixture
def stats_service():
    """Create a stats service instance."""
    return StatsService()


@pytest.fixture
def mock_models():
    """Create mock models."""
    mock_cacao_image = Mock()
    mock_cacao_prediction = Mock()
    mock_finca = Mock()
    
    return {
        'CacaoImage': mock_cacao_image,
        'CacaoPrediction': mock_cacao_prediction,
        'Finca': mock_finca
    }


@pytest.fixture
def test_users_with_groups(db):
    """Create test users with groups for stats testing."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    
    user1 = User.objects.create_user(
        username=f'user1_{unique_id}',
        email=f'user1_{unique_id}@test.com',
        password='pass'
    )
    user2 = User.objects.create_user(
        username=f'user2_{unique_id}',
        email=f'user2_{unique_id}@test.com',
        password='pass'
    )
    inactive_user = User.objects.create_user(
        username=f'inactive_{unique_id}',
        email=f'inactive_{unique_id}@test.com',
        password='pass',
        is_active=False
    )
    staff = User.objects.create_user(
        username=f'staff_{unique_id}',
        email=f'staff_{unique_id}@test.com',
        password='pass'
    )
    staff.is_staff = True
    staff.save()
    
    admin_user = User.objects.create_superuser(
        username=f'admin_{unique_id}',
        email=f'admin_{unique_id}@test.com',
        password='pass'
    )
    
    # Create farmer group and assign to user1
    farmer_group, _ = Group.objects.get_or_create(name='farmer')
    user1.groups.add(farmer_group)
    
    return {
        'user1': user1,
        'user2': user2,
        'inactive_user': inactive_user,
        'staff': staff,
        'admin_user': admin_user,
        'farmer_group': farmer_group,
        'unique_id': unique_id
    }


@pytest.mark.django_db
class TestStatsService:
    """Tests for StatsService."""
    
    def test_get_user_stats(self, stats_service, test_users_with_groups):
        """Test getting user statistics."""
        # Users are already created in the fixture
        
        stats = stats_service.get_user_stats()
        
        assert stats['total'] >= 5
        assert stats['active'] >= 4
        assert stats['staff'] >= 1
        assert stats['superusers'] >= 1
        assert stats['farmers'] >= 1
        assert 'this_week' in stats
        assert 'this_month' in stats
    
    def test_get_image_stats_no_images(self, stats_service, mock_models):
        """Test getting image statistics when no images exist."""
        with patch.object(stats_service, 'CacaoImage', None):
            stats = stats_service.get_image_stats()
            
            assert stats['total'] == 0
            assert stats['processed'] == 0
            assert stats['unprocessed'] == 0
            assert stats['processing_rate'] == 0
    
    def test_get_image_stats_with_images(self, stats_service):
        """Test getting image statistics with images."""
        with patch.object(stats_service, 'CacaoImage') as mock_image:
            mock_queryset = Mock()
            mock_image.objects = mock_queryset
            
            mock_queryset.count.return_value = 100
            mock_queryset.filter.return_value.count.return_value = 80
            
            stats = stats_service.get_image_stats()
            
            assert stats['total'] == 100
            assert stats['processed'] == 80
            assert stats['unprocessed'] == 20
            assert stats['processing_rate'] == 80.0
    
    def test_get_prediction_stats_no_predictions(self, stats_service):
        """Test getting prediction statistics when no predictions exist."""
        with patch.object(stats_service, 'CacaoPrediction', None):
            stats = stats_service.get_prediction_stats()
            
            assert stats['total'] == 0
            assert stats['average_confidence'] == 0
            assert 'average_dimensions' in stats
    
    def test_get_prediction_stats_with_predictions(self, stats_service):
        """Test getting prediction statistics with predictions."""
        with patch.object(stats_service, 'CacaoPrediction') as mock_prediction:
            mock_queryset = Mock()
            mock_prediction.objects = mock_queryset
            
            mock_queryset.count.return_value = 50
            
            # Mock aggregate
            mock_queryset.aggregate.return_value = {
                'avg_alto': 25.5,
                'avg_ancho': 20.3,
                'avg_grosor': 15.2,
                'avg_peso': 8.5,
                'avg_processing_time': 150.0,
                'avg_confidence': 0.85
            }
            
            # Mock annotate for quality distribution
            mock_annotated = Mock()
            mock_queryset.annotate.return_value = mock_annotated
            mock_annotated.filter.return_value.count.side_effect = [20, 15, 10, 5]
            
            stats = stats_service.get_prediction_stats()
            
            assert stats['total'] == 50
            assert stats['average_confidence'] == 0.85
            assert 'quality_distribution' in stats
    
    def test_get_activity_by_day(self, stats_service):
        """Test getting activity by day statistics."""
        with patch.object(stats_service, 'CacaoImage') as mock_image:
            mock_image.objects = Mock()
            # Create a chain of mocks that returns an iterable (empty list for this test)
            mock_values_list = []
            mock_annotate2 = Mock()
            mock_annotate2.values_list = Mock(return_value=mock_values_list)
            mock_values = Mock()
            mock_values.annotate = Mock(return_value=mock_annotate2)
            mock_annotate1 = Mock()
            mock_annotate1.values = Mock(return_value=mock_values)
            mock_filter = Mock()
            mock_filter.annotate = Mock(return_value=mock_annotate1)
            mock_image.objects.filter = Mock(return_value=mock_filter)
            
            stats = stats_service.get_activity_by_day(max_days=7)
            
            assert 'labels' in stats
            assert 'data' in stats
            assert len(stats['labels']) == 7
            assert len(stats['data']) == 7
    
    def test_get_finca_stats_no_fincas(self, stats_service):
        """Test getting finca statistics when no fincas exist."""
        with patch.object(stats_service, 'Finca', None):
            stats = stats_service.get_finca_stats()
            
            assert stats['total'] == 0
            assert stats['this_week'] == 0
            assert stats['this_month'] == 0
    
    def test_get_finca_stats_with_fincas(self, stats_service):
        """Test getting finca statistics with fincas."""
        with patch.object(stats_service, 'Finca') as mock_finca:
            mock_queryset = Mock()
            mock_finca.objects = mock_queryset
            
            mock_queryset.count.return_value = 25
            mock_queryset.filter.return_value.count.return_value = 5
            
            stats = stats_service.get_finca_stats()
            
            assert stats['total'] == 25
            assert stats['this_week'] == 5
    
    def test_get_top_regions(self, stats_service):
        """Test getting top regions."""
        with patch.object(stats_service, 'CacaoImage') as mock_image:
            mock_queryset = Mock()
            mock_image.objects = mock_queryset
            
            # Mock the chain: values -> annotate -> order_by -> __getitem__ (slice)
            mock_order_by = Mock()
            mock_annotate = Mock()
            mock_values = Mock()
            
            # Configure __getitem__ to return list when called with slice
            result_list = [
                {'region': 'Region1', 'count': 10},
                {'region': 'Region2', 'count': 5}
            ]
            mock_order_by.__getitem__ = Mock(return_value=result_list)
            mock_annotate.order_by = Mock(return_value=mock_order_by)
            mock_values.annotate = Mock(return_value=mock_annotate)
            mock_queryset.values = Mock(return_value=mock_values)
            
            regions = stats_service.get_top_regions(limit=10)
            
            assert isinstance(regions, list)
    
    def test_get_top_fincas(self, stats_service):
        """Test getting top fincas."""
        with patch.object(stats_service, 'CacaoImage') as mock_image:
            mock_queryset = Mock()
            mock_image.objects = mock_queryset
            
            # Mock the chain: values -> annotate -> order_by -> __getitem__ (slice)
            mock_order_by = Mock()
            mock_annotate = Mock()
            mock_values = Mock()
            
            # Configure __getitem__ to return list when called with slice
            result_list = [
                {'finca': 1, 'count': 10},
                {'finca': 2, 'count': 5}
            ]
            mock_order_by.__getitem__ = Mock(return_value=result_list)
            mock_annotate.order_by = Mock(return_value=mock_order_by)
            mock_values.annotate = Mock(return_value=mock_annotate)
            mock_queryset.values = Mock(return_value=mock_values)
            
            fincas = stats_service.get_top_fincas(limit=10)
            
            assert isinstance(fincas, list)
    
    def test_get_all_stats(self, stats_service):
        """Test getting all statistics."""
        with patch.object(stats_service, 'get_user_stats', return_value={'total': 10}):
            with patch.object(stats_service, 'get_image_stats', return_value={'total': 20}):
                with patch.object(stats_service, 'get_prediction_stats', return_value={'total': 30, 'quality_distribution': {}}):
                    with patch.object(stats_service, 'get_activity_by_day', return_value={'labels': [], 'data': []}):
                        with patch.object(stats_service, 'get_finca_stats', return_value={'total': 5}):
                            with patch.object(stats_service, 'get_top_regions', return_value=[]):
                                with patch.object(stats_service, 'get_top_fincas', return_value=[]):
                                    stats = stats_service.get_all_stats()
                                    
                                    assert 'users' in stats
                                    assert 'images' in stats
                                    assert 'predictions' in stats
                                    assert 'fincas' in stats
                                    assert 'generated_at' in stats
    
    def test_get_all_stats_with_error(self, stats_service):
        """Test getting all statistics when error occurs."""
        with patch.object(stats_service, 'get_user_stats', side_effect=Exception("Error")):
            stats = stats_service.get_all_stats()
            
            # Should return empty stats
            assert 'users' in stats
            assert stats['users']['total'] == 0
    
    def test_get_empty_stats(self, stats_service):
        """Test getting empty statistics structure."""
        stats = stats_service.get_empty_stats()
        
        assert 'users' in stats
        assert 'images' in stats
        assert 'predictions' in stats
        assert 'fincas' in stats
        assert stats['users']['total'] == 0
        assert stats['images']['total'] == 0
        assert stats['predictions']['total'] == 0
        assert stats['fincas']['total'] == 0

