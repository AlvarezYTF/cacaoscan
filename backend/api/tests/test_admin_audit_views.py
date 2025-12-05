"""
Tests for admin audit views.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.test import RequestFactory
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from rest_framework.response import Response
from api.views.admin.audit_views import (
    ActivityLogListView,
    LoginHistoryListView,
    AuditStatsView
)


@pytest.fixture
def activity_log_mock():
    """Mock ActivityLog model."""
    from unittest.mock import MagicMock
    mock_model = MagicMock()
    mock_model.objects = MagicMock()
    mock_model.DoesNotExist = Exception
    return mock_model


@pytest.fixture
def login_history_mock():
    """Mock LoginHistory model."""
    from unittest.mock import MagicMock
    mock_model = MagicMock()
    mock_model.objects = MagicMock()
    mock_model.DoesNotExist = Exception
    return mock_model


@pytest.mark.django_db
class TestActivityLogListView:
    """Test cases for ActivityLogListView."""
    
    def test_get_without_admin_permission(self, user):
        """Test GET request without admin permission."""
        factory = RequestFactory()
        request = factory.get('/api/admin/audit/logs/')
        request.user = user
        
        view = ActivityLogListView()
        response = view.get(request)
        
        assert response.status_code == 403
    
    def test_get_with_admin_permission(self, admin_user):
        """Test GET request with admin permission."""
        factory = RequestFactory()
        request = factory.get('/api/admin/audit/logs/')
        request.user = admin_user
        
        with patch('api.views.admin.audit_views.ActivityLog') as mock_activity_log:
            mock_queryset = Mock()
            mock_queryset.select_related.return_value = mock_queryset
            mock_queryset.order_by.return_value = mock_queryset
            mock_queryset.filter.return_value = mock_queryset
            mock_activity_log.objects.all.return_value = mock_queryset
            mock_activity_log.is_None = False
            
            with patch.object(ActivityLogListView, 'paginate_queryset') as mock_paginate:
                mock_response = Response({}, status=200)
                mock_paginate.return_value = mock_response
                
                view = ActivityLogListView()
                response = view.get(request)
                
                assert response.status_code == 200
    
    def test_get_with_filters(self, admin_user):
        """Test GET request with filters."""
        factory = RequestFactory()
        request = factory.get('/api/admin/audit/logs/?usuario=test&accion=create&fecha_desde=2024-01-01')
        request.user = admin_user
        
        with patch('api.views.admin.audit_views.ActivityLog') as mock_activity_log:
            mock_queryset = Mock()
            mock_queryset.select_related.return_value = mock_queryset
            mock_queryset.order_by.return_value = mock_queryset
            mock_queryset.filter.return_value = mock_queryset
            mock_activity_log.objects.all.return_value = mock_queryset
            mock_activity_log.is_None = False
            
            with patch.object(ActivityLogListView, 'paginate_queryset') as mock_paginate:
                mock_response = Response({}, status=200)
                mock_paginate.return_value = mock_response
                
                view = ActivityLogListView()
                response = view.get(request)
                
                assert response.status_code == 200
    
    def test_get_with_invalid_date_format(self, admin_user):
        """Test GET request with invalid date format."""
        factory = RequestFactory()
        request = factory.get('/api/admin/audit/logs/?fecha_desde=invalid-date')
        request.user = admin_user
        
        with patch('api.views.admin.audit_views.ActivityLog') as mock_activity_log:
            mock_activity_log.is_None = False
            mock_queryset = Mock()
            mock_queryset.select_related.return_value = mock_queryset
            mock_queryset.order_by.return_value = mock_queryset
            mock_queryset.filter.return_value = mock_queryset
            mock_activity_log.objects.all.return_value = mock_queryset
            
            view = ActivityLogListView()
            response = view.get(request)
            
            assert response.status_code == 400
    
    def test_get_with_activity_log_none(self, admin_user):
        """Test GET request when ActivityLog model is None."""
        factory = RequestFactory()
        request = factory.get('/api/admin/audit/logs/')
        request.user = admin_user
        
        with patch('api.views.admin.audit_views.ActivityLog', None):
            view = ActivityLogListView()
            response = view.get(request)
            
            assert response.status_code == 200
            assert response.data['count'] == 0


@pytest.mark.django_db
class TestLoginHistoryListView:
    """Test cases for LoginHistoryListView."""
    
    def test_get_without_admin_permission(self, user):
        """Test GET request without admin permission."""
        factory = RequestFactory()
        request = factory.get('/api/admin/audit/logins/')
        request.user = user
        
        view = LoginHistoryListView()
        response = view.get(request)
        
        assert response.status_code == 403
    
    def test_get_with_admin_permission(self, admin_user):
        """Test GET request with admin permission."""
        from audit.models import LoginHistory
        
        factory = RequestFactory()
        request = factory.get('/api/admin/audit/logins/')
        request.user = admin_user
        
        with patch.object(LoginHistoryListView, 'paginate_queryset') as mock_paginate:
            mock_response = Response({}, status=200)
            mock_paginate.return_value = mock_response
            
            view = LoginHistoryListView()
            response = view.get(request)
            
            assert response.status_code == 200
    
    def test_get_with_filters(self, admin_user):
        """Test GET request with filters."""
        factory = RequestFactory()
        request = factory.get('/api/admin/audit/logins/?usuario=test&success=true&fecha_desde=2024-01-01')
        request.user = admin_user
        
        with patch.object(LoginHistoryListView, 'paginate_queryset') as mock_paginate:
            mock_response = Response({}, status=200)
            mock_paginate.return_value = mock_response
            
            view = LoginHistoryListView()
            response = view.get(request)
            
            assert response.status_code == 200
    
    def test_get_with_invalid_date_format(self, admin_user):
        """Test GET request with invalid date format."""
        factory = RequestFactory()
        request = factory.get('/api/admin/audit/logins/?fecha_desde=invalid-date')
        request.user = admin_user
        
        view = LoginHistoryListView()
        response = view.get(request)
        
        assert response.status_code == 400


@pytest.mark.django_db
class TestAuditStatsView:
    """Test cases for AuditStatsView."""
    
    def test_get_without_admin_permission(self, user):
        """Test GET request without admin permission."""
        factory = RequestFactory()
        request = factory.get('/api/admin/audit/stats/')
        request.user = user
        
        view = AuditStatsView()
        response = view.get(request)
        
        assert response.status_code == 403
    
    def test_get_with_admin_permission(self, admin_user):
        """Test GET request with admin permission."""
        from audit.models import ActivityLog, LoginHistory
        from django.db.models import Count
        from datetime import timedelta
        
        factory = RequestFactory()
        request = factory.get('/api/admin/audit/stats/')
        request.user = admin_user
        
        with patch('api.views.admin.audit_views.ActivityLog') as mock_activity_log:
            with patch('api.views.admin.audit_views.LoginHistory') as mock_login_history:
                # Ensure ActivityLog is not None
                mock_activity_log.is_None = False
                # Mock ActivityLog queries - configure multiple return values for different calls
                mock_activity_log.objects.count.return_value = 100
                
                # For filter().count()
                mock_filter_result = Mock()
                mock_filter_result.count.return_value = 10
                mock_activity_log.objects.filter.return_value = mock_filter_result
                
                # For values('action').annotate().values_list()
                mock_action_values = Mock()
                mock_action_annotate = Mock()
                mock_action_annotate.values_list.return_value = [('create', 50), ('update', 30), ('delete', 20)]
                mock_action_values.annotate.return_value = mock_action_annotate
                
                # For values('resource_type').annotate().values_list()
                mock_resource_values = Mock()
                mock_resource_annotate = Mock()
                mock_resource_annotate.values_list.return_value = [('Finca', 30), ('Lote', 20)]
                mock_resource_values.annotate.return_value = mock_resource_annotate
                
                # For values('user__username').annotate().order_by()[:10]
                mock_user_values = Mock()
                mock_user_annotate = Mock()
                mock_user_order = Mock()
                # Configure __getitem__ to return list when sliced
                mock_user_order.__getitem__ = Mock(return_value=[{'user__username': 'testuser', 'count': 5}])
                mock_user_annotate.order_by.return_value = mock_user_order
                mock_user_values.annotate.return_value = mock_user_annotate
                
                # Configure values() to return different mocks based on argument
                def values_side_effect(*args, **kwargs):
                    if 'action' in args:
                        return mock_action_values
                    elif 'resource_type' in args:
                        return mock_resource_values
                    elif 'user__username' in args:
                        return mock_user_values
                    return Mock()
                
                mock_activity_log.objects.values.side_effect = values_side_effect
                
                # Mock LoginHistory queries
                mock_login_history.objects.count.return_value = 200
                
                # For filter().count() - multiple calls (for successful_logins, failed_logins, and day_logins)
                mock_login_filter = Mock()
                mock_login_filter.count.return_value = 180
                
                # For aggregate() - return dict with avg_duration
                from datetime import timedelta
                mock_avg_duration = timedelta(minutes=30)
                mock_session_filter = Mock()
                mock_session_filter.aggregate.return_value = {'avg_duration': mock_avg_duration}
                
                # Make filter return different mocks based on the filter condition
                def login_filter_side_effect(*args, **kwargs):
                    if 'session_duration__isnull' in kwargs:
                        return mock_session_filter
                    return mock_login_filter
                mock_login_history.objects.filter.side_effect = login_filter_side_effect
                
                # For values('ip_address').annotate().order_by()[:10]
                mock_ip_values = Mock()
                mock_ip_annotate = Mock()
                mock_ip_order = Mock()
                # Configure __getitem__ to return list when sliced
                mock_ip_order.__getitem__ = Mock(return_value=[{'ip_address': '127.0.0.1', 'count': 50}])
                mock_ip_annotate.order_by.return_value = mock_ip_order
                mock_ip_values.annotate.return_value = mock_ip_annotate
                mock_login_history.objects.values.return_value = mock_ip_values
                
                view = AuditStatsView()
                response = view.get(request)
                
                assert response.status_code == 200
                assert 'activity_log' in response.data
                assert 'login_history' in response.data
                assert 'generated_at' in response.data
    
    def test_get_with_exception(self, admin_user):
        """Test GET request with exception."""
        factory = RequestFactory()
        request = factory.get('/api/admin/audit/stats/')
        request.user = admin_user
        
        with patch('api.views.admin.audit_views.ActivityLog') as mock_activity_log:
            mock_activity_log.objects.count.side_effect = Exception('Database error')
            
            view = AuditStatsView()
            response = view.get(request)
            
            assert response.status_code == 500
            assert 'error' in response.data

