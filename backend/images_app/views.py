"""
Vistas para la gestión de imágenes de cacao.
"""
from typing import Optional, Tuple
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .models import CacaoImage
from .serializers import CacaoImageSerializer


class CacaoImageUploadView(APIView):
    """
    Vista para subir múltiples imágenes de cacao.
    """
    permission_classes = [IsAuthenticated]
    
    def _validate_file_size(self, image_file) -> Optional[str]:
        """Valida el tamaño del archivo."""
        max_size = 20 * 1024 * 1024  # 20MB
        if image_file.size > max_size:
            return 'El archivo excede el tamaño máximo de 20MB'
        return None
    
    def _validate_file_type(self, image_file) -> Optional[str]:
        """Valida el tipo de archivo."""
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
        if image_file.content_type not in allowed_types:
            return f'Tipo de archivo no permitido. Permitidos: {", ".join(allowed_types)}'
        return None
    
    def _assign_finca(self, cacao_image, finca_id):
        """Asigna la finca a la imagen si se proporciona."""
        if finca_id:
            try:
                from fincas_app.models import Finca
                finca = Finca.objects.get(id=finca_id)
                cacao_image.finca = finca
            except Finca.DoesNotExist:
                pass
    
    def _process_single_image(self, req
    
    6uest, image_file, idx: int) -> Tuple[Optional[dict], Optional[dict]]:
        """Procesa una sola imagen."""
        try:
            size_error = self._validate_file_size(image_file)
            if size_error:
                return None, {'file': image_file.name, 'error': size_error}
            
            type_error = self._validate_file_type(image_file)
            if type_error:
                return None, {'file': image_file.name, 'error': type_error}
            
            cacao_image = CacaoImage(
                user=request.user,
                image=image_file,
                file_name=image_file.name,
                file_size=image_file.size,
                file_type=image_file.content_type,
                processed=False
            )
            
            finca_id = request.data.get('finca_id')
            self._assign_finca(cacao_image, finca_id)
            
            cacao_image.save()
            
            serializer = CacaoImageSerializer(cacao_image, context={'request': request})
            return serializer.data, None
            
        except Exception as e:
            file_name = image_file.name if hasattr(image_file, 'name') else f'imagen_{idx}'
            return None, {'file': file_name, 'error': str(e)}
    
    def _determine_http_status(self, uploaded_count: int, errors_count: int) -> int:
        """Determina el código de estado HTTP."""
        if uploaded_count > 0:
            if errors_count > 0:
                return status.HTTP_207_MULTI_STATUS
            return status.HTTP_201_CREATED
        return status.HTTP_400_BAD_REQUEST
    
    def post(self, request):
        """
        Sube múltiples imágenes de cacao.
        
        Permite subir una o varias imágenes en una sola petición.
        Las imágenes se almacenan en AWS S3 (si está configurado) o localmente.
        """
        images = request.FILES.getlist('images')
        
        if not images:
            return Response(
                {'error': 'No se proporcionaron imágenes'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        uploaded = []
        errors = []
        
        for idx, image_file in enumerate(images):
            result, error = self._process_single_image(request, image_file, idx)
            if result:
                uploaded.append(result)
            else:
                errors.append(error)
        
        response_data = {
            'uploaded': uploaded,
            'total_uploaded': len(uploaded),
            'total_errors': len(errors)
        }
        
        if errors:
            response_data['errors'] = errors
        
        http_status = self._determine_http_status(len(uploaded), len(errors))
        return Response(response_data, status=http_status)


class CacaoImageListView(APIView):
    """
    Vista para listar imágenes de cacao del usuario autenticado.
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Get queryset ordered by created_at descending.
        """
        return CacaoImage.objects.order_by("-created_at")
    
    def get(self, request):
        """
        Lista todas las imágenes de cacao del usuario autenticado.
        Ordenadas por created_at descendente (más recientes primero).
        """
        queryset = self.get_queryset().filter(user=request.user)
        serializer = CacaoImageSerializer(queryset, many=True, context={'request': request})
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        }, status=status.HTTP_200_OK)
