"""
Admin permission mixin for API views.
"""
from typing import Optional
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status


class AdminPermissionMixin:
    """
    Mixin that provides admin permission checking functionality.
    
    Usage:
        class MyAdminView(AdminPermissionMixin, APIView):
            def get(self, request):
                # Check admin permission
                self.check_admin_permission(request.user)
                
                # Or use the helper method
                if not self.is_admin_user(request.user):
                    return self.admin_permission_denied()
    """
    
    def is_admin_user(self, user: User) -> bool:
        """
        Check if a user is an administrator.
        
        Args:
            user: User to check
            
        Returns:
            bool: True if user is admin (superuser or staff), False otherwise
        """
        if not user or not user.is_authenticated:
            return False
        return user.is_superuser or user.is_staff
    
    def check_admin_permission(self, user: User) -> None:
        """
        Check admin permission and raise exception if not admin.
        
        Args:
            user: User to check
            
        Raises:
            PermissionDenied: If user is not admin
        """
        if not self.is_admin_user(user):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("No tienes permisos de administrador para acceder a esta funcionalidad")
    
    def admin_permission_denied(self, message: Optional[str] = None) -> Response:
        """
        Return a standard 403 response for admin permission denied.
        
        Args:
            message: Optional custom error message
            
        Returns:
            Response with 403 status
        """
        error_message = message or 'No tienes permisos para acceder a esta funcionalidad'
        return Response({
            'error': error_message,
            'status': 'error'
        }, status=status.HTTP_403_FORBIDDEN)

