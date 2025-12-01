"""
Tests unitarios para api.middleware.

Cubre las clases de middleware:
- AuditMiddleware
- LoginAuditMiddleware
- TokenCleanupMiddleware
- Funciones helper: log_custom_activity, log_failed_login
"""
from unittest.mock import Mock, MagicMock, patch
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils import timezone

from api.middleware import (
    AuditMiddleware,
    LoginAuditMiddleware,
    TokenCleanupMiddleware,
    log_custom_activity,
    log_failed_login
)


class MiddlewareTestCase(TestCase):
    """Tests para middleware de auditoría."""

    def setUp(self):
        """Set up test fixtures."""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Mock get_response function
        self.get_response = Mock(return_value=HttpResponse(status=200))

    def test_audit_middleware_get_client_ip_from_forwarded(self):
        """Test AuditMiddleware gets IP from X-Forwarded-For header."""
        middleware = AuditMiddleware(self.get_response)
        
        request = self.factory.get('/api/test/')
        request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1, 10.0.0.1'
        
        ip = middleware.get_client_ip(request)
        
        self.assertEqual(ip, '192.168.1.1')

    def test_audit_middleware_get_client_ip_from_remote_addr(self):
        """Test AuditMiddleware gets IP from REMOTE_ADDR when no forwarded header."""
        middleware = AuditMiddleware(self.get_response)
        
        request = self.factory.get('/api/test/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        ip = middleware.get_client_ip(request)
        
        self.assertEqual(ip, '127.0.0.1')

    def test_audit_middleware_determine_post_action_login(self):
        """Test AuditMiddleware determines login action for POST to /login/."""
        middleware = AuditMiddleware(self.get_response)
        
        request = self.factory.post('/api/auth/login/')
        action = middleware._determine_post_action(request.path)
        
        self.assertEqual(action, 'login')

    def test_audit_middleware_determine_post_action_register(self):
        """Test AuditMiddleware determines create action for POST to /register/."""
        middleware = AuditMiddleware(self.get_response)
        
        request = self.factory.post('/api/auth/register/')
        action = middleware._determine_post_action(request.path)
        
        self.assertEqual(action, 'create')

    def test_audit_middleware_determine_post_action_upload(self):
        """Test AuditMiddleware determines upload action for POST to /images/."""
        middleware = AuditMiddleware(self.get_response)
        
        request = self.factory.post('/api/images/upload/')
        action = middleware._determine_post_action(request.path)
        
        self.assertEqual(action, 'upload')

    def test_audit_middleware_determine_get_action_download(self):
        """Test AuditMiddleware determines download action for GET to /download/."""
        middleware = AuditMiddleware(self.get_response)
        
        request = self.factory.get('/api/download/file/')
        action = middleware._determine_get_action(request.path)
        
        self.assertEqual(action, 'download')

    def test_audit_middleware_determine_get_action_view(self):
        """Test AuditMiddleware determines view action for GET to /stats/."""
        middleware = AuditMiddleware(self.get_response)
        
        request = self.factory.get('/api/stats/')
        action = middleware._determine_get_action(request.path)
        
        self.assertEqual(action, 'view')

    def test_audit_middleware_determine_action_post(self):
        """Test AuditMiddleware determine_action for POST method."""
        middleware = AuditMiddleware(self.get_response)
        
        request = self.factory.post('/api/auth/login/')
        action = middleware.determine_action(request)
        
        self.assertEqual(action, 'login')

    def test_audit_middleware_determine_action_put(self):
        """Test AuditMiddleware determine_action for PUT method."""
        middleware = AuditMiddleware(self.get_response)
        
        request = self.factory.put('/api/fincas/1/')
        action = middleware.determine_action(request)
        
        self.assertEqual(action, 'update')

    def test_audit_middleware_determine_action_delete(self):
        """Test AuditMiddleware determine_action for DELETE method."""
        middleware = AuditMiddleware(self.get_response)
        
        request = self.factory.delete('/api/fincas/1/')
        action = middleware.determine_action(request)
        
        self.assertEqual(action, 'delete')

    def test_audit_middleware_determine_model_finca(self):
        """Test AuditMiddleware determines Finca model from path."""
        middleware = AuditMiddleware(self.get_response)
        
        request = self.factory.get('/api/fincas/')
        model = middleware.determine_model(request)
        
        self.assertEqual(model, 'Finca')

    def test_audit_middleware_determine_model_lote(self):
        """Test AuditMiddleware determines Lote model from path."""
        middleware = AuditMiddleware(self.get_response)
        
        request = self.factory.get('/api/lotes/')
        model = middleware.determine_model(request)
        
        self.assertEqual(model, 'Lote')

    def test_audit_middleware_determine_model_unknown(self):
        """Test AuditMiddleware returns Unknown for unrecognized path."""
        middleware = AuditMiddleware(self.get_response)
        
        request = self.factory.get('/api/unknown/')
        model = middleware.determine_model(request)
        
        self.assertEqual(model, 'Unknown')

    def test_audit_middleware_extract_object_id_from_path(self):
        """Test AuditMiddleware extracts object ID from path."""
        middleware = AuditMiddleware(self.get_response)
        
        request = self.factory.get('/api/fincas/123/')
        object_id = middleware.extract_object_id(request)
        
        self.assertEqual(object_id, '123')

    def test_audit_middleware_extract_object_id_no_id(self):
        """Test AuditMiddleware returns None when no ID in path."""
        middleware = AuditMiddleware(self.get_response)
        
        request = self.factory.get('/api/fincas/')
        object_id = middleware.extract_object_id(request)
        
        self.assertIsNone(object_id)

    def test_audit_middleware_create_description(self):
        """Test AuditMiddleware creates activity description."""
        middleware = AuditMiddleware(self.get_response)
        
        request = self.factory.get('/api/fincas/')
        request.user = self.user
        
        description = middleware.create_description(request, 'view', 'Finca')
        
        self.assertIn('testuser', description)
        self.assertIn('visualizó', description)
        self.assertIn('Finca', description)

    @patch('api.middleware.ActivityLog')
    def test_audit_middleware_logs_activity_for_authenticated_user(self, mock_activity_log):
        """Test AuditMiddleware logs activity for authenticated user."""
        middleware = AuditMiddleware(self.get_response)
        
        request = self.factory.get('/api/fincas/')
        request.user = self.user
        request.user.is_authenticated = True
        request.audit_action = 'view'
        request.audit_info = {
            'ip_address': '127.0.0.1',
            'user_agent': 'TestAgent'
        }
        
        middleware.log_activity(request)
        
        mock_activity_log.log_activity.assert_called_once()

    @patch('api.middleware.ActivityLog')
    def test_audit_middleware_does_not_log_for_unauthenticated(self, mock_activity_log):
        """Test AuditMiddleware does not log for unauthenticated users."""
        middleware = AuditMiddleware(self.get_response)
        
        request = self.factory.get('/api/fincas/')
        request.user = Mock()
        request.user.is_authenticated = False
        
        response = middleware(request)
        
        mock_activity_log.log_activity.assert_not_called()

    @patch('api.middleware.ActivityLog')
    def test_audit_middleware_does_not_log_for_error_responses(self, mock_activity_log):
        """Test AuditMiddleware does not log for error responses."""
        middleware = AuditMiddleware(lambda req: HttpResponse(status=500))
        
        request = self.factory.get('/api/fincas/')
        request.user = self.user
        request.user.is_authenticated = True
        
        response = middleware(request)
        
        mock_activity_log.log_activity.assert_not_called()

    def test_login_audit_middleware_get_client_ip(self):
        """Test LoginAuditMiddleware gets client IP."""
        middleware = LoginAuditMiddleware(self.get_response)
        
        request = self.factory.get('/api/test/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        ip = middleware.get_client_ip(request)
        
        self.assertEqual(ip, '127.0.0.1')

    @patch('api.middleware.LoginHistory')
    def test_login_audit_middleware_logs_login(self, mock_login_history):
        """Test LoginAuditMiddleware logs login."""
        middleware = LoginAuditMiddleware(self.get_response)
        
        request = self.factory.get('/api/test/')
        request.user = self.user
        request.META['HTTP_USER_AGENT'] = 'TestAgent'
        
        middleware.log_login(request)
        
        mock_login_history.log_login.assert_called_once()

    @patch('api.middleware.LoginHistory')
    def test_login_audit_middleware_logs_logout(self, mock_login_history):
        """Test LoginAuditMiddleware logs logout."""
        middleware = LoginAuditMiddleware(self.get_response)
        
        request = self.factory.post('/api/auth/logout/')
        request.user = self.user
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        middleware.log_logout(request)
        
        mock_login_history.log_logout.assert_called_once()

    def test_token_cleanup_middleware_passes_through(self):
        """Test TokenCleanupMiddleware passes request through unchanged."""
        middleware = TokenCleanupMiddleware(self.get_response)
        
        request = self.factory.get('/api/test/')
        response = middleware(request)
        
        self.get_response.assert_called_once_with(request)
        self.assertEqual(response.status_code, 200)

    @patch('api.middleware.ActivityLog')
    @patch('api.middleware.logger')
    def test_log_custom_activity(self, mock_logger, mock_activity_log):
        """Test log_custom_activity function."""
        log_custom_activity(
            user=self.user,
            action='test_action',
            model='TestModel',
            description='Test description',
            object_id='123',
            ip_address='127.0.0.1',
            user_agent='TestAgent'
        )
        
        mock_activity_log.log_activity.assert_called_once()
        mock_logger.info.assert_called_once()

    @patch('api.middleware.LoginHistory')
    @patch('api.middleware.logger')
    def test_log_failed_login(self, mock_logger, mock_login_history):
        """Test log_failed_login function."""
        log_failed_login(
            username='testuser',
            ip_address='127.0.0.1',
            user_agent='TestAgent',
            failure_reason='Invalid password'
        )
        
        mock_login_history.log_login.assert_called_once()
        mock_logger.warning.assert_called_once()

    @patch('api.middleware.logger')
    def test_audit_middleware_handles_exception(self, mock_logger):
        """Test AuditMiddleware handles exceptions gracefully."""
        def failing_get_response(request):
            raise Exception("Test error")
        
        middleware = AuditMiddleware(failing_get_response)
        
        request = self.factory.get('/api/test/')
        
        with self.assertRaises(Exception):
            middleware(request)
        
        # Should not crash the middleware itself

