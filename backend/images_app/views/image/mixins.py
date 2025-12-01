"""
Image permission mixins.
"""
from api.utils.model_imports import get_models_safely
from api.views.mixins.admin_mixin import AdminPermissionMixin

# Import models safely
models = get_models_safely({
    'CacaoImage': 'images_app.models.CacaoImage',
})
CacaoImage = models['CacaoImage']


class ImagePermissionMixin(AdminPermissionMixin):
    """
    Mixin para manejar permisos de acceso a imágenes.
    """
    
    def can_access_image(self, user, image):
        """
        Verificar si el usuario puede acceder a la imagen.
        
        Args:
            user: Usuario autenticado
            image: Objeto CacaoImage
            
        Returns:
            bool: True si puede acceder, False en caso contrario
        """
        # El propietario siempre puede acceder
        if image.user == user:
            return True
        
        # Los admins pueden acceder a cualquier imagen
        if self.is_admin_user(user):
            return True
        
        # Los analistas pueden acceder a imágenes de todos los usuarios
        if user.groups.filter(name='analyst').exists():
            return True
        
        return False
    
    def get_user_images_queryset(self, user):
        """
        Obtener queryset de imágenes según permisos del usuario.
        Optimizado con select_related y prefetch_related para evitar N+1 queries.
        
        Args:
            user: Usuario autenticado
            
        Returns:
            QuerySet: Queryset filtrado según permisos
        """
        base_queryset = CacaoImage.objects.select_related(
            'user',
            'finca',
            'finca__agricultor',
            'lote',
            'lote__finca',
            'lote__finca__agricultor'
        ).prefetch_related('prediction')
        
        if self.is_admin_user(user):
            # Admins pueden ver todas las imágenes
            return base_queryset
        elif user.groups.filter(name='analyst').exists():
            # Analistas pueden ver todas las imágenes
            return base_queryset
        else:
            # Agricultores solo ven sus propias imágenes
            return base_queryset.filter(user=user)

