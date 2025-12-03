"""
Tests for BaseService and ServiceResult.
"""
import pytest
from unittest.mock import patch, MagicMock
from django.contrib.auth.models import User
from django.core.paginator import Paginator

from api.services.base import (
    BaseService,
    ServiceResult,
    ServiceError,
    ValidationServiceError,
    PermissionServiceError,
    NotFoundServiceError
)


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def admin_user():
    """Create an admin user."""
    return User.objects.create_user(
        username='admin',
        email='admin@example.com',
        password='adminpass123',
        is_staff=True,
        is_superuser=True
    )


@pytest.mark.django_db
class TestBaseService:
    """Tests for BaseService."""

    def test_log_info(self):
        """Test info logging."""
        service = BaseService()
        service.log_info("Test message", extra={'key': 'value'})
        
        # Should not raise exception
        assert True

    def test_log_warning(self):
        """Test warning logging."""
        service = BaseService()
        service.log_warning("Test warning", extra={'key': 'value'})
        
        # Should not raise exception
        assert True

    def test_log_error(self):
        """Test error logging."""
        service = BaseService()
        service.log_error("Test error", extra={'key': 'value'})
        
        # Should not raise exception
        assert True

    def test_validate_user_permission_admin(self, admin_user):
        """Test permission validation for admin user."""
        service = BaseService()
        
        result = service.validate_user_permission(admin_user, 'test_permission')
        
        assert result is True

    def test_validate_user_permission_regular_user(self, user):
        """Test permission validation for regular user."""
        service = BaseService()
        
        result = service.validate_user_permission(user, 'test_permission')
        
        assert result is False

    def test_check_user_permission_admin(self, admin_user):
        """Test check permission for admin user."""
        service = BaseService()
        
        # Should not raise exception
        service.check_user_permission(admin_user, 'test_permission')

    def test_check_user_permission_regular_user(self, user):
        """Test check permission for regular user raises exception."""
        service = BaseService()
        
        with pytest.raises(PermissionServiceError):
            service.check_user_permission(user, 'test_permission')

    def test_validate_required_fields_success(self):
        """Test validating required fields when all present."""
        service = BaseService()
        
        data = {'field1': 'value1', 'field2': 'value2', 'field3': 'value3'}
        required_fields = ['field1', 'field2']
        
        # Should not raise exception
        service.validate_required_fields(data, required_fields)

    def test_validate_required_fields_missing(self):
        """Test validating required fields when missing."""
        service = BaseService()
        
        data = {'field1': 'value1'}
        required_fields = ['field1', 'field2', 'field3']
        
        with pytest.raises(ValidationServiceError) as exc_info:
            service.validate_required_fields(data, required_fields)
        
        assert 'field2' in str(exc_info.value) or 'field3' in str(exc_info.value)

    def test_validate_required_fields_none_value(self):
        """Test validating required fields when value is None."""
        service = BaseService()
        
        data = {'field1': 'value1', 'field2': None}
        required_fields = ['field1', 'field2']
        
        with pytest.raises(ValidationServiceError):
            service.validate_required_fields(data, required_fields)

    def test_validate_field_type_success(self):
        """Test validating field type when correct."""
        service = BaseService()
        
        # Should not raise exception
        service._validate_field_type('test_field', 123, int)

    def test_validate_field_type_failure(self):
        """Test validating field type when incorrect."""
        service = BaseService()
        
        with pytest.raises(ValidationServiceError) as exc_info:
            service._validate_field_type('test_field', '123', int)
        
        assert 'tipo' in str(exc_info.value).lower() or 'type' in str(exc_info.value).lower()

    def test_validate_field_range_min(self):
        """Test validating field range minimum."""
        service = BaseService()
        
        with pytest.raises(ValidationServiceError):
            service._validate_field_range('test_field', 5, {'min': 10})

    def test_validate_field_range_max(self):
        """Test validating field range maximum."""
        service = BaseService()
        
        with pytest.raises(ValidationServiceError):
            service._validate_field_range('test_field', 15, {'max': 10})

    def test_validate_field_length_min(self):
        """Test validating field length minimum."""
        service = BaseService()
        
        with pytest.raises(ValidationServiceError):
            service._validate_field_length('test_field', 'ab', {'min_length': 5})

    def test_validate_field_length_max(self):
        """Test validating field length maximum."""
        service = BaseService()
        
        with pytest.raises(ValidationServiceError):
            service._validate_field_length('test_field', 'very long string', {'max_length': 5})

    def test_validate_field_values_success(self):
        """Test validating field values when all valid."""
        service = BaseService()
        
        data = {
            'name': 'Test Name',
            'age': 25,
            'score': 85
        }
        validations = {
            'name': {'min_length': 2, 'max_length': 100},
            'age': {'type': int, 'min': 0, 'max': 150},
            'score': {'min': 0, 'max': 100}
        }
        
        # Should not raise exception
        service.validate_field_values(data, validations)

    def test_validate_field_values_failure(self):
        """Test validating field values when invalid."""
        service = BaseService()
        
        data = {'age': -5}
        validations = {'age': {'type': int, 'min': 0}}
        
        with pytest.raises(ValidationServiceError):
            service.validate_field_values(data, validations)

    def test_paginate_results_success(self):
        """Test paginating results successfully."""
        service = BaseService()
        
        # Create a mock queryset
        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 50
        
        # Mock paginator
        with patch('api.services.base.Paginator') as mock_paginator_class:
            mock_paginator = MagicMock()
            mock_page = MagicMock()
            mock_page.number = 1
            mock_page.has_next.return_value = True
            mock_page.has_previous.return_value = False
            mock_page.next_page_number.return_value = 2
            mock_page.previous_page_number.side_effect = Exception("No previous")
            mock_page.object_list = [f'item_{i}' for i in range(20)]
            mock_paginator.page.return_value = mock_page
            mock_paginator.num_pages = 3
            mock_paginator.count = 50
            mock_paginator_class.return_value = mock_paginator
            
            result = service.paginate_results(mock_queryset, page=1, page_size=20)
        
        assert 'results' in result
        assert 'pagination' in result
        assert result['pagination']['page'] == 1
        assert result['pagination']['total'] == 50

    def test_paginate_results_invalid_page(self):
        """Test paginating results with invalid page number."""
        service = BaseService()
        
        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 50
        
        with patch('api.services.base.Paginator') as mock_paginator_class:
            mock_paginator = MagicMock()
            mock_page = MagicMock()
            mock_page.number = 1
            mock_page.has_next.return_value = False
            mock_page.has_previous.return_value = False
            mock_page.object_list = []
            mock_paginator.page.side_effect = [Exception("Invalid page"), mock_page]
            mock_paginator.num_pages = 1
            mock_paginator.count = 50
            mock_paginator_class.return_value = mock_paginator
            
            result = service.paginate_results(mock_queryset, page=999, page_size=20)
        
        # Should default to page 1
        assert result['pagination']['page'] == 1

    def test_create_audit_log_success(self, user):
        """Test creating audit log successfully."""
        service = BaseService()
        
        with patch('api.services.base.ActivityLog') as mock_activity_log:
            mock_activity_log.objects.create.return_value = MagicMock()
            
            service.create_audit_log(
                user=user,
                action='test_action',
                resource_type='test_resource',
                resource_id=1,
                details={'test': 'data'}
            )
        
        # Should not raise exception
        assert True

    def test_create_audit_log_import_error(self, user):
        """Test creating audit log when import fails."""
        service = BaseService()
        
        with patch('api.services.base.ActivityLog', side_effect=ImportError("Module not found")):
            # Should not raise exception, just log warning
            service.create_audit_log(
                user=user,
                action='test_action',
                resource_type='test_resource'
            )
        
        assert True

    def test_execute_with_transaction_success(self):
        """Test executing function within transaction successfully."""
        service = BaseService()
        
        def test_func(x, y):
            return x + y
        
        result = service.execute_with_transaction(test_func, 5, 3)
        
        assert result == 8

    def test_execute_with_transaction_error(self):
        """Test executing function within transaction when error occurs."""
        service = BaseService()
        
        def test_func():
            raise ValueError("Test error")
        
        with pytest.raises(ServiceError):
            service.execute_with_transaction(test_func)


@pytest.mark.django_db
class TestServiceResult:
    """Tests for ServiceResult."""

    def test_success_creation(self):
        """Test creating successful result."""
        result = ServiceResult.success(data={'key': 'value'}, message="Success")
        
        assert result.success is True
        assert result.data == {'key': 'value'}
        assert result.message == "Success"
        assert result.error is None

    def test_error_creation(self):
        """Test creating error result."""
        error = ValidationServiceError("Test error")
        result = ServiceResult.error(error, message="Error occurred")
        
        assert result.success is False
        assert result.error == error
        assert result.message == "Error occurred"

    def test_validation_error(self):
        """Test creating validation error result."""
        result = ServiceResult.validation_error("Validation failed", details={'field': 'test'})
        
        assert result.success is False
        assert isinstance(result.error, ValidationServiceError)
        assert result.error.details == {'field': 'test'}

    def test_permission_error(self):
        """Test creating permission error result."""
        result = ServiceResult.permission_error("Permission denied")
        
        assert result.success is False
        assert isinstance(result.error, PermissionServiceError)

    def test_not_found_error(self):
        """Test creating not found error result."""
        result = ServiceResult.not_found_error("Resource not found")
        
        assert result.success is False
        assert isinstance(result.error, NotFoundServiceError)

    def test_to_dict_success(self):
        """Test converting success result to dict."""
        result = ServiceResult.success(data={'key': 'value'}, message="Success")
        
        result_dict = result.to_dict()
        
        assert result_dict['success'] is True
        assert result_dict['data'] == {'key': 'value'}
        assert result_dict['message'] == "Success"
        assert 'error' not in result_dict

    def test_to_dict_error(self):
        """Test converting error result to dict."""
        error = ValidationServiceError("Test error", error_code="test_code", details={'key': 'value'})
        result = ServiceResult.error(error)
        
        result_dict = result.to_dict()
        
        assert result_dict['success'] is False
        assert 'error' in result_dict
        assert result_dict['error']['message'] == "Test error"
        assert result_dict['error']['code'] == "test_code"
        assert result_dict['error']['details'] == {'key': 'value'}


@pytest.mark.django_db
class TestServiceErrors:
    """Tests for ServiceError classes."""

    def test_service_error_creation(self):
        """Test creating ServiceError."""
        error = ServiceError("Test error", error_code="test_code", details={'key': 'value'})
        
        assert str(error) == "Test error"
        assert error.error_code == "test_code"
        assert error.details == {'key': 'value'}

    def test_validation_service_error(self):
        """Test creating ValidationServiceError."""
        error = ValidationServiceError("Validation failed", details={'field': 'test'})
        
        assert isinstance(error, ServiceError)
        assert str(error) == "Validation failed"

    def test_permission_service_error(self):
        """Test creating PermissionServiceError."""
        error = PermissionServiceError("Permission denied", error_code="permission_denied")
        
        assert isinstance(error, ServiceError)
        assert error.error_code == "permission_denied"

    def test_not_found_service_error(self):
        """Test creating NotFoundServiceError."""
        error = NotFoundServiceError("Not found", details={'resource_id': 123})
        
        assert isinstance(error, ServiceError)
        assert error.details == {'resource_id': 123}

