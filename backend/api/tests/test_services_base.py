"""
Tests for base service classes.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.db import transaction
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
from django.utils import timezone
from api.services.base import (
    BaseService,
    ServiceResult,
    ServiceError,
    ValidationServiceError,
    PermissionServiceError,
    NotFoundServiceError
)


class TestServiceError:
    """Test cases for ServiceError."""
    
    def test_service_error_creation(self):
        """Test creating a ServiceError."""
        error = ServiceError('Test error')
        assert str(error) == 'Test error'
        assert error.message == 'Test error'
        assert error.error_code is None
        assert error.details == {}
    
    def test_service_error_with_error_code(self):
        """Test ServiceError with error code."""
        error = ServiceError('Test error', error_code='TEST_ERROR')
        assert error.error_code == 'TEST_ERROR'
    
    def test_service_error_with_details(self):
        """Test ServiceError with details."""
        details = {'field': 'username', 'reason': 'already exists'}
        error = ServiceError('Test error', details=details)
        assert error.details == details


class TestValidationServiceError:
    """Test cases for ValidationServiceError."""
    
    def test_validation_service_error(self):
        """Test creating a ValidationServiceError."""
        error = ValidationServiceError('Validation failed')
        assert isinstance(error, ServiceError)
        assert error.message == 'Validation failed'


class TestPermissionServiceError:
    """Test cases for PermissionServiceError."""
    
    def test_permission_service_error(self):
        """Test creating a PermissionServiceError."""
        error = PermissionServiceError('Permission denied')
        assert isinstance(error, ServiceError)
        assert error.message == 'Permission denied'


class TestNotFoundServiceError:
    """Test cases for NotFoundServiceError."""
    
    def test_not_found_service_error(self):
        """Test creating a NotFoundServiceError."""
        error = NotFoundServiceError('Resource not found')
        assert isinstance(error, ServiceError)
        assert error.message == 'Resource not found'


class TestBaseService:
    """Test cases for BaseService."""
    
    def test_base_service_initialization(self):
        """Test BaseService initialization."""
        service = BaseService()
        assert service.logger is not None
        assert 'BaseService' in service.logger.name
    
    def test_log_info(self):
        """Test log_info method."""
        service = BaseService()
        with patch.object(service.logger, 'info') as mock_info:
            service.log_info('Test message')
            mock_info.assert_called_once_with('Test message', extra={})
    
    def test_log_warning(self):
        """Test log_warning method."""
        service = BaseService()
        with patch.object(service.logger, 'warning') as mock_warning:
            service.log_warning('Test warning')
            mock_warning.assert_called_once_with('Test warning', extra={})
    
    def test_log_error(self):
        """Test log_error method."""
        service = BaseService()
        with patch.object(service.logger, 'error') as mock_error:
            service.log_error('Test error')
            mock_error.assert_called_once_with('Test error', extra={})
    
    def test_log_debug(self):
        """Test log_debug method."""
        service = BaseService()
        with patch.object(service.logger, 'debug') as mock_debug:
            service.log_debug('Test debug')
            mock_debug.assert_called_once_with('Test debug', extra={})
    
    def test_validate_user_permission_superuser(self, admin_user):
        """Test validate_user_permission with superuser."""
        service = BaseService()
        assert service.validate_user_permission(admin_user, 'any_permission') is True
    
    def test_validate_user_permission_staff(self, staff_user):
        """Test validate_user_permission with staff user."""
        service = BaseService()
        assert service.validate_user_permission(staff_user, 'any_permission') is True
    
    def test_validate_user_permission_regular_user(self, user):
        """Test validate_user_permission with regular user."""
        service = BaseService()
        assert service.validate_user_permission(user, 'any_permission') is False
    
    def test_check_user_permission_superuser(self, admin_user):
        """Test check_user_permission with superuser."""
        service = BaseService()
        # Should not raise
        service.check_user_permission(admin_user, 'any_permission')
    
    def test_check_user_permission_regular_user(self, user):
        """Test check_user_permission with regular user raises error."""
        service = BaseService()
        with pytest.raises(PermissionServiceError):
            service.check_user_permission(user, 'any_permission')
    
    def test_validate_required_fields_success(self):
        """Test validate_required_fields with all required fields."""
        service = BaseService()
        data = {'field1': 'value1', 'field2': 'value2'}
        required_fields = ['field1', 'field2']
        # Should not raise
        service.validate_required_fields(data, required_fields)
    
    def test_validate_required_fields_missing(self):
        """Test validate_required_fields with missing fields."""
        service = BaseService()
        data = {'field1': 'value1'}
        required_fields = ['field1', 'field2']
        with pytest.raises(ValidationServiceError) as exc_info:
            service.validate_required_fields(data, required_fields)
        assert 'field2' in exc_info.value.message
    
    def test_validate_required_fields_none_value(self):
        """Test validate_required_fields with None value."""
        service = BaseService()
        data = {'field1': 'value1', 'field2': None}
        required_fields = ['field1', 'field2']
        with pytest.raises(ValidationServiceError):
            service.validate_required_fields(data, required_fields)
    
    def test_validate_field_type_success(self):
        """Test _validate_field_type with correct type."""
        service = BaseService()
        service._validate_field_type('test_field', 'value', str)
        # Should not raise
    
    def test_validate_field_type_failure(self):
        """Test _validate_field_type with incorrect type."""
        service = BaseService()
        with pytest.raises(ValidationServiceError) as exc_info:
            service._validate_field_type('test_field', 123, str)
        assert 'test_field' in exc_info.value.message
    
    def test_validate_field_range_min(self):
        """Test _validate_field_range with value below minimum."""
        service = BaseService()
        with pytest.raises(ValidationServiceError):
            service._validate_field_range('test_field', 5, {'min': 10})
    
    def test_validate_field_range_max(self):
        """Test _validate_field_range with value above maximum."""
        service = BaseService()
        with pytest.raises(ValidationServiceError):
            service._validate_field_range('test_field', 15, {'max': 10})
    
    def test_validate_field_range_success(self):
        """Test _validate_field_range with valid range."""
        service = BaseService()
        service._validate_field_range('test_field', 10, {'min': 5, 'max': 15})
        # Should not raise
    
    def test_validate_field_length_min(self):
        """Test _validate_field_length with value below minimum length."""
        service = BaseService()
        with pytest.raises(ValidationServiceError):
            service._validate_field_length('test_field', 'abc', {'min_length': 5})
    
    def test_validate_field_length_max(self):
        """Test _validate_field_length with value above maximum length."""
        service = BaseService()
        with pytest.raises(ValidationServiceError):
            service._validate_field_length('test_field', 'abcdefghij', {'max_length': 5})
    
    def test_validate_field_length_success(self):
        """Test _validate_field_length with valid length."""
        service = BaseService()
        service._validate_field_length('test_field', 'abcde', {'min_length': 3, 'max_length': 10})
        # Should not raise
    
    def test_validate_field_values(self):
        """Test validate_field_values with various validations."""
        service = BaseService()
        data = {'name': 'test', 'age': 25, 'description': 'test description'}
        validations = {
            'name': {'type': str, 'min_length': 3},
            'age': {'type': int, 'min': 18, 'max': 100}
        }
        service.validate_field_values(data, validations)
        # Should not raise
    
    def test_execute_with_transaction_success(self):
        """Test execute_with_transaction with successful function."""
        service = BaseService()
        
        def test_func(x, y):
            return x + y
        
        result = service.execute_with_transaction(test_func, 2, 3)
        assert result == 5
    
    def test_execute_with_transaction_exception(self):
        """Test execute_with_transaction with exception."""
        service = BaseService()
        
        def test_func():
            raise ValueError('Test error')
        
        with pytest.raises(ServiceError) as exc_info:
            service.execute_with_transaction(test_func)
        assert 'operación' in str(exc_info.value.message).lower() or 'transacción' in str(exc_info.value.message).lower()
    
    def test_paginate_results_success(self):
        """Test paginate_results with valid page."""
        service = BaseService()
        queryset = Mock()
        queryset.count.return_value = 100
        
        mock_page = Mock()
        mock_page.object_list = list(range(10))
        mock_page.number = 1
        mock_page.has_next.return_value = True
        mock_page.has_previous.return_value = False
        mock_page.next_page_number.return_value = 2
        mock_page.previous_page_number.side_effect = EmptyPage('No previous page')
        
        with patch('django.core.paginator.Paginator') as mock_paginator_class:
            mock_paginator = Mock()
            mock_paginator.count = 100
            mock_paginator.num_pages = 10
            mock_paginator.page.return_value = mock_page
            mock_paginator_class.return_value = mock_paginator
            
            result = service.paginate_results(queryset, page=1, page_size=10)
            
            assert 'results' in result
            assert 'pagination' in result
            assert result['pagination']['page'] == 1
            assert result['pagination']['total'] == 100
    
    def test_paginate_results_invalid_page(self):
        """Test paginate_results with invalid page."""
        service = BaseService()
        queryset = Mock()
        
        mock_page = Mock()
        mock_page.object_list = list(range(10))
        mock_page.number = 1
        mock_page.has_next.return_value = False
        mock_page.has_previous.return_value = False
        
        with patch('django.core.paginator.Paginator') as mock_paginator_class:
            mock_paginator = Mock()
            mock_paginator.count = 100
            mock_paginator.num_pages = 10
            # Simulate invalid page
            mock_paginator.page.side_effect = [InvalidPage('Invalid page'), mock_page]
            mock_paginator_class.return_value = mock_paginator
            
            result = service.paginate_results(queryset, page=999, page_size=10)
            
            assert result['pagination']['page'] == 1
    
    def test_create_audit_log_success(self, user):
        """Test create_audit_log with available audit model."""
        service = BaseService()
        
        mock_activity_log = Mock()
        mock_activity_log.objects = Mock()
        mock_activity_log.objects.create = Mock()
        
        with patch('audit.models.ActivityLog', mock_activity_log):
            with patch('django.db.transaction.on_commit') as mock_on_commit:
                # Capture the callback function
                callback_capture = []
                def capture_callback(callback):
                    callback_capture.append(callback)
                mock_on_commit.side_effect = capture_callback
                
                service.create_audit_log(
                    user=user,
                    action='test_action',
                    resource_type='test_resource',
                    resource_id=123,
                    details={'key': 'value'}
                )
                
                # Verify on_commit was called
                assert len(callback_capture) == 1
                # Execute the callback to verify it works
                callback_capture[0]()
                mock_activity_log.objects.create.assert_called_once()
    
    def test_create_audit_log_model_not_available(self, user):
        """Test create_audit_log when audit model is not available."""
        service = BaseService()
        
        # Patch the import to raise ImportError
        with patch('builtins.__import__', side_effect=ImportError("No module named 'audit'")):
            with patch('django.db.transaction.on_commit') as mock_on_commit:
                callback_capture = []
                def capture_callback(callback):
                    callback_capture.append(callback)
                mock_on_commit.side_effect = capture_callback
                
                with patch.object(service, 'log_debug') as mock_debug:
                    service.create_audit_log(
                        user=user,
                        action='test_action',
                        resource_type='test_resource'
                    )
                    # Execute the callback to trigger log_debug
                    assert len(callback_capture) == 1
                    callback_capture[0]()
                    # The code should call log_debug when import fails
                    mock_debug.assert_called_once()
    
    def test_create_audit_log_exception(self, user):
        """Test create_audit_log with exception."""
        service = BaseService()
        
        mock_activity_log = Mock()
        mock_activity_log.objects = Mock()
        mock_activity_log.objects.create.side_effect = Exception('Database error')
        
        with patch('audit.models.ActivityLog', mock_activity_log):
            with patch('django.db.transaction.on_commit') as mock_on_commit:
                callback_capture = []
                def capture_callback(callback):
                    callback_capture.append(callback)
                mock_on_commit.side_effect = capture_callback
                
                with patch.object(service, 'log_warning') as mock_warning:
                    service.create_audit_log(
                        user=user,
                        action='test_action',
                        resource_type='test_resource'
                    )
                    # Execute the callback to trigger the exception
                    assert len(callback_capture) == 1
                    callback_capture[0]()
                    mock_warning.assert_called_once()


class TestServiceResult:
    """Test cases for ServiceResult."""
    
    def test_service_result_success_creation(self):
        """Test creating a successful ServiceResult."""
        result = ServiceResult.success(data={'key': 'value'}, message='Success')
        assert result.success is True
        assert result.data == {'key': 'value'}
        assert result.message == 'Success'
        assert result.error is None
    
    def test_service_result_error_creation(self):
        """Test creating an error ServiceResult."""
        error = ServiceError('Test error')
        result = ServiceResult.error(error, message='Operation failed')
        assert result.success is False
        assert result.error == error
        assert result.message == 'Operation failed'
    
    def test_service_result_validation_error(self):
        """Test creating a validation error ServiceResult."""
        result = ServiceResult.validation_error('Validation failed', details={'field': 'email'})
        assert result.success is False
        assert isinstance(result.error, ValidationServiceError)
        assert result.error.message == 'Validation failed'
        assert result.error.details == {'field': 'email'}
    
    def test_service_result_permission_error(self):
        """Test creating a permission error ServiceResult."""
        result = ServiceResult.permission_error('Permission denied')
        assert result.success is False
        assert isinstance(result.error, PermissionServiceError)
        assert result.error.message == 'Permission denied'
    
    def test_service_result_not_found_error(self):
        """Test creating a not found error ServiceResult."""
        result = ServiceResult.not_found_error('Resource not found')
        assert result.success is False
        assert isinstance(result.error, NotFoundServiceError)
        assert result.error.message == 'Resource not found'
    
    def test_service_result_to_dict_success(self):
        """Test to_dict with successful result."""
        result = ServiceResult.success(data={'key': 'value'}, message='Success')
        result_dict = result.to_dict()
        assert result_dict['success'] is True
        assert result_dict['data'] == {'key': 'value'}
        assert result_dict['message'] == 'Success'
        assert 'error' not in result_dict
    
    def test_service_result_to_dict_error(self):
        """Test to_dict with error result."""
        error = ServiceError('Test error', error_code='TEST_ERROR', details={'key': 'value'})
        result = ServiceResult.error(error)
        result_dict = result.to_dict()
        assert result_dict['success'] is False
        assert 'error' in result_dict
        assert result_dict['error']['message'] == 'Test error'
        assert result_dict['error']['code'] == 'TEST_ERROR'
        assert result_dict['error']['details'] == {'key': 'value'}

