"""
Tests for admin permission mixin.
"""
import pytest
from unittest.mock import Mock
from django.contrib.auth.models import User
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import status
from api.views.mixins.admin_mixin import AdminPermissionMixin


class TestAdminPermissionMixin:
    """Test cases for AdminPermissionMixin."""
    
    def test_is_admin_user_with_superuser(self, admin_user):
        """Test is_admin_user returns True for superuser."""
        mixin = AdminPermissionMixin()
        assert mixin.is_admin_user(admin_user) is True
    
    def test_is_admin_user_with_staff(self, staff_user):
        """Test is_admin_user returns True for staff user."""
        mixin = AdminPermissionMixin()
        assert mixin.is_admin_user(staff_user) is True
    
    def test_is_admin_user_with_regular_user(self, user):
        """Test is_admin_user returns False for regular user."""
        mixin = AdminPermissionMixin()
        assert mixin.is_admin_user(user) is False
    
    def test_is_admin_user_with_none(self):
        """Test is_admin_user returns False for None."""
        mixin = AdminPermissionMixin()
        assert mixin.is_admin_user(None) is False
    
    def test_is_admin_user_with_unauthenticated(self):
        """Test is_admin_user returns False for unauthenticated user."""
        mixin = AdminPermissionMixin()
        unauthenticated_user = Mock()
        unauthenticated_user.is_authenticated = False
        assert mixin.is_admin_user(unauthenticated_user) is False
    
    def test_check_admin_permission_with_superuser(self, admin_user):
        """Test check_admin_permission does not raise for superuser."""
        mixin = AdminPermissionMixin()
        mixin.check_admin_permission(admin_user)
    
    def test_check_admin_permission_with_staff(self, staff_user):
        """Test check_admin_permission does not raise for staff."""
        mixin = AdminPermissionMixin()
        mixin.check_admin_permission(staff_user)
    
    def test_check_admin_permission_with_regular_user(self, user):
        """Test check_admin_permission raises PermissionDenied for regular user."""
        mixin = AdminPermissionMixin()
        with pytest.raises(PermissionDenied):
            mixin.check_admin_permission(user)
    
    def test_check_admin_permission_with_none(self):
        """Test check_admin_permission raises PermissionDenied for None."""
        mixin = AdminPermissionMixin()
        with pytest.raises(PermissionDenied):
            mixin.check_admin_permission(None)
    
    def test_admin_permission_denied_default_message(self):
        """Test admin_permission_denied returns 403 with default message."""
        mixin = AdminPermissionMixin()
        response = mixin.admin_permission_denied()
        
        assert isinstance(response, Response)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data['error'] == 'No tienes permisos para acceder a esta funcionalidad'
        assert response.data['status'] == 'error'
    
    def test_admin_permission_denied_custom_message(self):
        """Test admin_permission_denied returns 403 with custom message."""
        mixin = AdminPermissionMixin()
        custom_message = 'Custom error message'
        response = mixin.admin_permission_denied(custom_message)
        
        assert isinstance(response, Response)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data['error'] == custom_message
        assert response.data['status'] == 'error'
    
    def test_admin_permission_denied_with_none_message(self):
        """Test admin_permission_denied with None message uses default."""
        mixin = AdminPermissionMixin()
        response = mixin.admin_permission_denied(None)
        
        assert isinstance(response, Response)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data['error'] == 'No tienes permisos para acceder a esta funcionalidad'
        assert response.data['status'] == 'error'

