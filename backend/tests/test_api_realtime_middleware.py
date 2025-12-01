"""
Tests unitarios para api.realtime_middleware.

Cubre las clases de middleware:
- RealtimeAuditMiddleware
- RealtimeLoginMiddleware
"""
from unittest.mock import Mock, MagicMock, patch
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils import timezone

from api.realtime_middleware import (
    RealtimeAuditMiddleware,
    RealtimeLoginMiddleware
)


class RealtimeMiddlewareTestCase(TestCase):
    """Tests para middleware de tiempo real."""

    def setUp(self):
        """Set up test fixtures."""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.get_response = Mock(return_value=HttpResponse(status=200))

    def test_realtime_audit_middleware_get_client_ip(self):
        """Test RealtimeAuditMiddleware gets client IP."""
        middleware = RealtimeAuditMiddleware(self.get_response)
        
        request = self.factory.get('/api/test/')
        request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1'
        
        ip = middleware.get_client_ip(request)
        
        self.assertEqual(ip, '192.168.1.1')

    def test_realtime_audit_middleware_get_action_type_get(self):
        """Test RealtimeAuditMiddleware determines action type for GET."""
        middleware = RealtimeAuditMiddleware(self.get_response)
        
        action = middleware.get_action_type('GET')
        
        self.assertEqual(action, 'view')

    def test_realtime_audit_middleware_get_action_type_post(self):
        """Test RealtimeAuditMiddleware determines action type for POST."""
        middleware = RealtimeAuditMiddleware(self.get_response)
        
        action = middleware.get_action_type('POST')
        
        self.assertEqual(action, 'create')

    def test_realtime_audit_middleware_get_action_type_put(self):
        """Test RealtimeAuditMiddleware determines action type for PUT."""
        middleware = RealtimeAuditMiddleware(self.get_response)
        
        action = middleware.get_action_type('PUT')
        
        self.assertEqual(action, 'update')

    def test_realtime_audit_middleware_get_action_type_delete(self):
        """Test RealtimeAuditMiddleware determines action type for DELETE."""
        middleware = RealtimeAuditMiddleware(self.get_response)
        
        action = middleware.get_action_type('DELETE')
        
        self.assertEqual(action, 'delete')

    def test_realtime_audit_middleware_get_model_name_images(self):
        """Test RealtimeAuditMiddleware determines model from path."""
        middleware = RealtimeAuditMiddleware(self.get_response)
        
        model = middleware.get_model_name('/api/images/')
        
        self.assertEqual(model, 'CacaoImage')

    def test_realtime_audit_middleware_get_model_name_fincas(self):
        """Test RealtimeAuditMiddleware determines Finca model."""
        middleware = RealtimeAuditMiddleware(self.get_response)
        
        model = middleware.get_model_name('/api/fincas/')
        
        self.assertEqual(model, 'Finca')

    def test_realtime_audit_middleware_get_model_name_system(self):
        """Test RealtimeAuditMiddleware returns System for unknown path."""
        middleware = RealtimeAuditMiddleware(self.get_response)
        
        model = middleware.get_model_name('/unknown/')
        
        self.assertEqual(model, 'System')

    def test_realtime_audit_middleware_create_action_description_get(self):
        """Test RealtimeAuditMiddleware creates description for GET."""
        middleware = RealtimeAuditMiddleware(self.get_response)
        
        request = self.factory.get('/api/fincas/')
        description = middleware.create_action_description(request)
        
        self.assertIn('Visualización', description)
        self.assertIn('/api/fincas/', description)

    def test_realtime_audit_middleware_create_action_description_post(self):
        """Test RealtimeAuditMiddleware creates description for POST."""
        middleware = RealtimeAuditMiddleware(self.get_response)
        
        request = self.factory.post('/api/fincas/')
        description = middleware.create_action_description(request)
        
        self.assertIn('Creación', description)

    def test_realtime_audit_middleware_get_action_display(self):
        """Test RealtimeAuditMiddleware gets action display name."""
        middleware = RealtimeAuditMiddleware(self.get_response)
        
        display = middleware.get_action_display('view')
        
        self.assertEqual(display, 'Visualización')

    def test_realtime_audit_middleware_calculate_response_time(self):
        """Test RealtimeAuditMiddleware calculates response time."""
        middleware = RealtimeAuditMiddleware(self.get_response)
        
        request = self.factory.get('/api/test/')
        request._audit_start_time = timezone.now()
        
        # Wait a bit
        import time
        time.sleep(0.01)
        
        response_time = middleware.calculate_response_time(request)
        
        self.assertGreater(response_time, 0)

    def test_realtime_audit_middleware_calculate_response_time_no_start(self):
        """Test RealtimeAuditMiddleware returns 0 if no start time."""
        middleware = RealtimeAuditMiddleware(self.get_response)
        
        request = self.factory.get('/api/test/')
        response_time = middleware.calculate_response_time(request)
        
        self.assertEqual(response_time, 0)

    @patch('api.realtime_middleware.realtime_service')
    def test_realtime_audit_middleware_sends_activity_log(self, mock_realtime_service):
        """Test RealtimeAuditMiddleware sends activity log."""
        middleware = RealtimeAuditMiddleware(self.get_response)
        
        request = self.factory.get('/api/fincas/')
        request.user = self.user
        request.user.is_authenticated = True
        request._audit_start_time = timezone.now()
        
        response = middleware(request)
        
        mock_realtime_service.send_activity_log.assert_called_once()

    @patch('api.realtime_middleware.realtime_service')
    def test_realtime_audit_middleware_does_not_send_for_unauthenticated(self, mock_realtime_service):
        """Test RealtimeAuditMiddleware does not send for unauthenticated users."""
        middleware = RealtimeAuditMiddleware(self.get_response)
        
        request = self.factory.get('/api/fincas/')
        request.user = Mock()
        request.user.is_authenticated = False
        
        response = middleware(request)
        
        mock_realtime_service.send_activity_log.assert_not_called()

    def test_realtime_login_middleware_get_client_ip(self):
        """Test RealtimeLoginMiddleware gets client IP."""
        middleware = RealtimeLoginMiddleware(self.get_response)
        
        request = self.factory.get('/api/test/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        ip = middleware.get_client_ip(request)
        
        self.assertEqual(ip, '127.0.0.1')

    @patch('api.realtime_middleware.realtime_service')
    def test_realtime_login_middleware_sends_on_login_success(self, mock_realtime_service):
        """Test RealtimeLoginMiddleware sends login activity on success."""
        middleware = RealtimeLoginMiddleware(self.get_response)
        
        request = self.factory.post('/api/auth/login/')
        request._is_login_attempt = True
        request._login_ip = '127.0.0.1'
        request._login_user_agent = 'TestAgent'
        request.user = self.user
        request.user.is_authenticated = True
        
        response = Mock(status_code=200)
        middleware.get_response = Mock(return_value=response)
        
        result = middleware(request)
        
        mock_realtime_service.send_login_activity.assert_called_once()

    @patch('api.realtime_middleware.realtime_service')
    def test_realtime_login_middleware_sends_on_login_failure(self, mock_realtime_service):
        """Test RealtimeLoginMiddleware sends login activity on failure."""
        middleware = RealtimeLoginMiddleware(self.get_response)
        
        request = self.factory.post('/api/auth/login/')
        request._is_login_attempt = True
        request._login_ip = '127.0.0.1'
        request._login_user_agent = 'TestAgent'
        request.user = Mock()
        request.user.is_authenticated = False
        
        response = Mock(status_code=400)
        middleware.get_response = Mock(return_value=response)
        
        result = middleware(request)
        
        mock_realtime_service.send_login_activity.assert_called_once()

    @patch('api.realtime_middleware.realtime_service')
    def test_realtime_login_middleware_does_not_send_for_non_login(self, mock_realtime_service):
        """Test RealtimeLoginMiddleware does not send for non-login requests."""
        middleware = RealtimeLoginMiddleware(self.get_response)
        
        request = self.factory.get('/api/fincas/')
        
        response = middleware(request)
        
        mock_realtime_service.send_login_activity.assert_not_called()

    @patch('api.realtime_middleware.logger')
    def test_realtime_audit_middleware_handles_exception(self, mock_logger):
        """Test RealtimeAuditMiddleware handles exceptions gracefully."""
        def failing_get_response(request):
            raise Exception("Test error")
        
        middleware = RealtimeAuditMiddleware(failing_get_response)
        
        request = self.factory.get('/api/test/')
        request.user = self.user
        request.user.is_authenticated = True
        
        with self.assertRaises(Exception):
            middleware(request)
        
        # Should log error but not crash

