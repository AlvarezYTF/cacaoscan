"""
Serializers para imágenes de cacao.
"""
from rest_framework import serializers
from .models import CacaoImage


class CacaoImageSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo CacaoImage.
    """
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = CacaoImage
        fields = ['id', 'image', 'image_url', 'uploaded_at', 'finca', 'lote', 
                  'finca_nombre', 'region', 'variedad', 'fecha_cosecha', 'notas',
                  'file_name', 'file_size', 'file_type', 'processed', 'created_at']
        read_only_fields = ['id', 'uploaded_at', 'created_at']
    
    def get_image_url(self, obj):
        """
        Obtiene la URL completa de la imagen.
        """
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

