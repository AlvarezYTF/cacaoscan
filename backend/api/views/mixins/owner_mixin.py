"""
Owner permission mixin for API views.
Provides functionality to check if a user owns a resource.
"""
from typing import Optional, Any
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status


class OwnerPermissionMixin:
    """
    Mixin that provides owner permission checking functionality.
    
    Usage:
        class MyView(OwnerPermissionMixin, APIView):
            def get(self, request, resource_id):
                resource = MyModel.objects.get(id=resource_id)
                
                # Check owner permission
                if not self.is_owner(request.user, resource):
                    return self.owner_permission_denied()
                
                # Or use the helper method
                self.check_owner_permission(request.user, resource)
    """
    
    def get_owner_field(self) -> str:
        """
        Get the field name that contains the owner reference.
        Override this method in subclasses if the owner field is different.
        
        Returns:
            str: Field name for owner (default: 'user')
        """
        return 'user'
    
    def is_owner(self, user: User, resource: Any) -> bool:
        """
        Check if a user owns a resource.
        
        Args:
            user: User to check
            resource: Resource object to check ownership
            
        Returns:
            bool: True if user owns the resource, False otherwise
        """
        if not user or not user.is_authenticated:
            return False
        
        # Admins can access any resource
        if user.is_superuser or user.is_staff:
            return True
        
        # Check ownership
        owner_field = self.get_owner_field()
        owner = getattr(resource, owner_field, None)
        
        if owner is None:
            return False
        
        # Handle both User objects and user IDs
        if isinstance(owner, User):
            return owner.id == user.id
        else:
            return owner == user.id
    
    def check_owner_permission(self, user: User, resource: Any) -> None:
        """
        Check owner permission and raise exception if user is not owner.
        
        Args:
            user: User to check
            resource: Resource object to check ownership
            
        Raises:
            PermissionDenied: If user is not owner
        """
        if not self.is_owner(user, resource):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("No tienes permisos para acceder a este recurso")
    
    def owner_permission_denied(self, message: Optional[str] = None) -> Response:
        """
        Return a standard 403 response for owner permission denied.
        
        Args:
            message: Optional custom error message
            
        Returns:
            Response with 403 status
        """
        error_message = message or 'No tienes permisos para acceder a este recurso'
        return Response({
            'error': error_message,
            'status': 'error'
        }, status=status.HTTP_403_FORBIDDEN)
    
    def get_owner_queryset(self, user: User, queryset) -> Any:
        """
        Filter queryset to only include resources owned by the user.
        Admins can see all resources.
        
        Args:
            user: User to filter by
            queryset: QuerySet to filter
            
        Returns:
            Filtered QuerySet
        """
        if not user or not user.is_authenticated:
            return queryset.none()
        
        # Admins can see all resources
        if user.is_superuser or user.is_staff:
            return queryset
        
        # Filter by owner
        owner_field = self.get_owner_field()
        filter_kwargs = {owner_field: user}
        return queryset.filter(**filter_kwargs)

