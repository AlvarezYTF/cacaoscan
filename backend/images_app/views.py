"""
Vistas para la gestión de imágenes de cacao.
"""
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
            try:
                # Validar tamaño del archivo (máximo 20MB)
                max_size = 20 * 1024 * 1024  # 20MB
                if image_file.size > max_size:
                    errors.append({
                        'file': image_file.name,
                        'error': f'El archivo excede el tamaño máximo de 20MB'
                    })
                    continue
                
                # Validar tipo de archivo
                allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
                if image_file.content_type not in allowed_types:
                    errors.append({
                        'file': image_file.name,
                        'error': f'Tipo de archivo no permitido. Permitidos: {", ".join(allowed_types)}'
                    })
                    continue
                
                # Crear instancia de CacaoImage
                cacao_image = CacaoImage(
                    user=request.user,
                    image=image_file,
                    file_name=image_file.name,
                    file_size=image_file.size,
                    file_type=image_file.content_type,
                    processed=False
                )
                
                # Obtener finca_id si se proporciona
                finca_id = request.data.get('finca_id')
                if finca_id:
                    try:
                        from fincas_app.models import Finca
                        finca = Finca.objects.get(id=finca_id)
                        cacao_image.finca = finca
                    except Finca.DoesNotExist:
                        pass
                
                cacao_image.save()
                
                # Serializar la imagen subida
                serializer = CacaoImageSerializer(cacao_image, context={'request': request})
                uploaded.append(serializer.data)
                
            except Exception as e:
                errors.append({
                    'file': image_file.name if hasattr(image_file, 'name') else f'imagen_{idx}',
                    'error': str(e)
                })
        
        # Preparar respuesta
        response_data = {
            'uploaded': uploaded,
            'total_uploaded': len(uploaded),
            'total_errors': len(errors)
        }
        
        if errors:
            response_data['errors'] = errors
        
        # Determinar código de estado HTTP
        if len(uploaded) > 0:
            if len(errors) > 0:
                # Algunas imágenes se subieron, otras fallaron
                http_status = status.HTTP_207_MULTI_STATUS  # Multi-Status
            else:
                # Todas las imágenes se subieron correctamente
                http_status = status.HTTP_201_CREATED
        else:
            # Ninguna imagen se subió
            http_status = status.HTTP_400_BAD_REQUEST
        
        return Response(response_data, status=http_status)


class CacaoImageListView(APIView):
    """
    Vista para listar imágenes de cacao del usuario autenticado.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Lista todas las imágenes de cacao del usuario autenticado.
        """
        images = CacaoImage.objects.filter(user=request.user).order_by('-created_at')
        serializer = CacaoImageSerializer(images, many=True, context={'request': request})
        return Response({
            'count': images.count(),
            'results': serializer.data
        }, status=status.HTTP_200_OK)
