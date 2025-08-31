"""
Permisos personalizados para el sistema CacaoScan.

Este módulo define permisos específicos para diferentes roles de usuario
y operaciones del sistema, siguiendo el principio de menor privilegio.
"""

from rest_framework import permissions
from django.utils.translation import gettext_lazy as _


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado que permite solo a los propietarios editar sus objetos.
    Los usuarios autenticados pueden leer, pero solo el propietario puede escribir.
    """
    message = _("Solo puedes modificar tus propios recursos.")

    def has_object_permission(self, request, view, obj):
        # Permisos de lectura para cualquier usuario autenticado
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Permisos de escritura solo para el propietario
        if hasattr(obj, 'uploaded_by'):
            return obj.uploaded_by == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        
        # Si no hay relación de propiedad, denegar
        return False


class IsFarmerUser(permissions.BasePermission):
    """
    Permite acceso solo a usuarios con rol de agricultor.
    """
    message = _("Solo los agricultores pueden acceder a este recurso.")

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == 'farmer'
        )


class IsAnalystUser(permissions.BasePermission):
    """
    Permite acceso solo a usuarios con rol de analista.
    """
    message = _("Solo los analistas pueden acceder a este recurso.")

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == 'analyst'
        )


class IsAdminUser(permissions.BasePermission):
    """
    Permite acceso solo a usuarios con rol de administrador.
    """
    message = _("Solo los administradores pueden acceder a este recurso.")

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == 'admin'
        )


class IsVerifiedUser(permissions.BasePermission):
    """
    Permite acceso solo a usuarios verificados.
    """
    message = _("Tu cuenta debe estar verificada para acceder a este recurso.")

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.is_verified
        )


class IsAdminOrAnalyst(permissions.BasePermission):
    """
    Permite acceso a administradores y analistas.
    """
    message = _("Solo administradores y analistas pueden acceder a este recurso.")

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ['admin', 'analyst']
        )


class IsAdminOrOwner(permissions.BasePermission):
    """
    Permite acceso a administradores o al propietario del objeto.
    """
    message = _("Solo administradores o el propietario pueden acceder a este recurso.")

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Los administradores pueden hacer todo
        if request.user.role == 'admin':
            return True
        
        # Los propietarios pueden acceder a sus objetos
        if hasattr(obj, 'uploaded_by'):
            return obj.uploaded_by == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        
        return False


class CanUploadImages(permissions.BasePermission):
    """
    Permite subir imágenes solo a usuarios verificados (agricultores y administradores).
    """
    message = _("Solo usuarios verificados pueden subir imágenes.")

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.is_verified and
            request.user.role in ['farmer', 'admin']
        )


class CanViewPredictions(permissions.BasePermission):
    """
    Permite ver predicciones a usuarios autenticados.
    Los administradores y analistas ven todas, los agricultores solo las suyas.
    """
    message = _("No tienes permisos para ver estas predicciones.")

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Administradores y analistas ven todo
        if request.user.role in ['admin', 'analyst']:
            return True
        
        # Agricultores ven solo sus predicciones
        if request.user.role == 'farmer':
            return obj.uploaded_by == request.user
        
        return False


class CanManageDataset(permissions.BasePermission):
    """
    Permite gestionar el dataset solo a administradores y analistas.
    """
    message = _("Solo administradores y analistas pueden gestionar el dataset.")

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ['admin', 'analyst']
        )


class CanTrainModels(permissions.BasePermission):
    """
    Permite entrenar modelos solo a administradores.
    """
    message = _("Solo administradores pueden entrenar modelos.")

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == 'admin'
        )


class ReadOnlyForFarmers(permissions.BasePermission):
    """
    Permite solo lectura a agricultores, escritura completa a admin/analistas.
    """
    message = _("Los agricultores solo pueden consultar información.")

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Admin y analistas pueden hacer todo
        if request.user.role in ['admin', 'analyst']:
            return True
        
        # Agricultores solo pueden leer
        if request.user.role == 'farmer':
            return request.method in permissions.SAFE_METHODS
        
        return False


class IsSameUserOrAdmin(permissions.BasePermission):
    """
    Permite acceso al mismo usuario o a administradores.
    Útil para endpoints de perfil de usuario.
    """
    message = _("Solo puedes acceder a tu propio perfil.")

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Administradores pueden acceder a cualquier perfil
        if request.user.role == 'admin':
            return True
        
        # Los usuarios pueden acceder a su propio perfil
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'id'):
            return obj.id == request.user.id
        
        return False


class APIThrottlePermission(permissions.BasePermission):
    """
    Permiso base para implementar throttling por rol.
    """
    message = _("Has excedido el límite de solicitudes permitidas.")

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Los límites se aplican en el throttling, aquí solo verificamos autenticación
        return True


# Combinaciones comunes de permisos
class FarmerWritePermission(permissions.BasePermission):
    """
    Combina permisos para agricultores: autenticado, verificado y propietario.
    """
    message = _("Debes ser un agricultor verificado y propietario del recurso.")

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.is_verified and
            request.user.role == 'farmer'
        )

    def has_object_permission(self, request, view, obj):
        # Verificar propiedad del objeto
        if hasattr(obj, 'uploaded_by'):
            return obj.uploaded_by == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False


class AdminOrAnalystReadWritePermission(permissions.BasePermission):
    """
    Permite lectura y escritura completa a administradores y analistas.
    """
    message = _("Solo administradores y analistas pueden realizar esta acción.")

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ['admin', 'analyst']
        )


# Diccionario de permisos por rol para facilitar uso
ROLE_PERMISSIONS = {
    'farmer': [IsVerifiedUser, IsFarmerUser],
    'analyst': [IsAnalystUser],
    'admin': [IsAdminUser],
}

# Permisos para operaciones específicas
OPERATION_PERMISSIONS = {
    'upload_image': [CanUploadImages],
    'view_predictions': [CanViewPredictions], 
    'manage_dataset': [CanManageDataset],
    'train_models': [CanTrainModels],
    'view_all_users': [IsAdminOrAnalyst],
    'manage_users': [IsAdminUser],
}
