"""
Serializers para la app de imágenes de cacao.

Proporciona serialización y validación para las APIs REST de predicción
de características físicas de granos de cacao.
"""

import os
from rest_framework import serializers
from django.core.validators import FileExtensionValidator
from django.core.files.images import get_image_dimensions
from PIL import Image
import io

from .models import CacaoImage


class ImageUploadSerializer(serializers.Serializer):
    """
    Serializer para subida de imágenes para predicción.
    
    Valida la imagen y la prepara para el procesamiento ML.
    """
    
    image = serializers.ImageField(
        validators=[
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'tif']
            )
        ],
        help_text="Imagen del grano de cacao (formatos: JPG, PNG, BMP, TIFF)"
    )
    
    # Campos opcionales para metadatos
    batch_number = serializers.CharField(
        max_length=100, 
        required=False, 
        allow_blank=True,
        help_text="Número de lote del grano (opcional)"
    )
    
    origin = serializers.CharField(
        max_length=200, 
        required=False, 
        allow_blank=True,
        help_text="Origen geográfico del grano (opcional)"
    )
    
    notes = serializers.CharField(
        max_length=500, 
        required=False, 
        allow_blank=True,
        help_text="Notas adicionales sobre el grano (opcional)"
    )
    
    def validate_image(self, value):
        """
        Valida la imagen subida.
        
        Args:
            value: Archivo de imagen
            
        Returns:
            Archivo validado
            
        Raises:
            serializers.ValidationError: Si la imagen no es válida
        """
        # Verificar tamaño del archivo (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if value.size > max_size:
            raise serializers.ValidationError(
                f"El archivo es demasiado grande. Máximo permitido: {max_size // (1024*1024)}MB"
            )
        
        # Verificar dimensiones mínimas
        try:
            width, height = get_image_dimensions(value)
            if width < 32 or height < 32:
                raise serializers.ValidationError(
                    "La imagen es demasiado pequeña. Dimensiones mínimas: 32x32 píxeles"
                )
            
            # Verificar dimensiones máximas
            if width > 4096 or height > 4096:
                raise serializers.ValidationError(
                    "La imagen es demasiado grande. Dimensiones máximas: 4096x4096 píxeles"
                )
        except Exception:
            raise serializers.ValidationError(
                "No se pudo determinar las dimensiones de la imagen"
            )
        
        # Validar que se puede abrir con PIL
        try:
            # Resetear posición del archivo
            value.seek(0)
            
            # Intentar abrir con PIL
            with Image.open(value) as img:
                # Verificar que no esté corrupta
                img.verify()
                
            # Resetear posición nuevamente
            value.seek(0)
            
        except Exception as e:
            raise serializers.ValidationError(
                f"La imagen está corrupta o no es válida: {str(e)}"
            )
        
        return value
    
    def validate(self, attrs):
        """Validación global del serializer."""
        # Aquí se pueden agregar validaciones adicionales si es necesario
        return attrs


class CacaoImageSerializer(serializers.ModelSerializer):
    """
    Serializer completo para el modelo CacaoImage.
    
    Incluye todos los campos del modelo y campos calculados adicionales.
    """
    
    # Campos de solo lectura calculados
    aspect_ratio = serializers.SerializerMethodField()
    volume_estimate = serializers.SerializerMethodField() 
    density_estimate = serializers.SerializerMethodField()
    file_size_display = serializers.SerializerMethodField()
    is_defective = serializers.SerializerMethodField()
    quality_display = serializers.SerializerMethodField()
    
    # URL completa de la imagen
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = CacaoImage
        fields = [
            # Campos básicos
            'id',
            'image',
            'image_url',
            
            # Características físicas
            'width',
            'height', 
            'thickness',
            'weight',
            
            # Información de calidad
            'quality_score',
            'predicted_quality',
            'quality_display',
            'defect_type',
            'defect_confidence',
            'is_defective',
            
            # Metadatos de la imagen
            'image_width',
            'image_height', 
            'file_size',
            'file_size_display',
            
            # Información de procesamiento
            'is_processed',
            'processing_time',
            
            # Campos adicionales
            'batch_number',
            'origin',
            'harvest_date',
            'notes',
            
            # Campos calculados
            'aspect_ratio',
            'volume_estimate',
            'density_estimate',
            
            # Timestamps
            'created_at',
            'updated_at'
        ]
        
        read_only_fields = [
            'id',
            'width',
            'height',
            'thickness', 
            'weight',
            'quality_score',
            'predicted_quality',
            'defect_confidence',
            'image_width',
            'image_height',
            'file_size',
            'is_processed',
            'processing_time',
            'created_at',
            'updated_at',
            'aspect_ratio',
            'volume_estimate', 
            'density_estimate',
            'file_size_display',
            'is_defective',
            'quality_display',
            'image_url'
        ]
    
    def get_image_url(self, obj):
        """Obtiene la URL completa de la imagen."""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    def get_aspect_ratio(self, obj):
        """Calcula la relación de aspecto del grano."""
        return obj.aspect_ratio
    
    def get_volume_estimate(self, obj):
        """Obtiene la estimación de volumen."""
        return obj.volume_estimate
    
    def get_density_estimate(self, obj):
        """Obtiene la estimación de densidad."""
        return obj.density_estimate
    
    def get_file_size_display(self, obj):
        """Obtiene el tamaño del archivo en formato legible."""
        return obj.get_file_size_display()
    
    def get_is_defective(self, obj):
        """Determina si el grano tiene defectos."""
        return obj.is_defective()
    
    def get_quality_display(self, obj):
        """Obtiene la descripción de calidad con puntuación."""
        return obj.get_quality_display_with_score()


class PredictionResultSerializer(serializers.Serializer):
    """
    Serializer para los resultados de predicción ML.
    
    Formatea la respuesta de la predicción para la API.
    """
    
    # Información del registro
    id = serializers.IntegerField(help_text="ID del registro en la base de datos")
    
    # Características físicas predichas
    width = serializers.DecimalField(
        max_digits=8, 
        decimal_places=3,
        help_text="Ancho del grano en milímetros"
    )
    
    height = serializers.DecimalField(
        max_digits=8,
        decimal_places=3, 
        help_text="Alto del grano en milímetros"
    )
    
    thickness = serializers.DecimalField(
        max_digits=8,
        decimal_places=3,
        help_text="Grosor del grano en milímetros"
    )
    
    predicted_weight = serializers.DecimalField(
        max_digits=8,
        decimal_places=4,
        help_text="Peso predicho del grano en gramos"
    )
    
    # Información adicional de la predicción
    prediction_method = serializers.CharField(
        help_text="Método usado para la predicción de peso"
    )
    
    confidence_level = serializers.CharField(
        help_text="Nivel de confianza de la predicción"
    )
    
    confidence_score = serializers.DecimalField(
        max_digits=5,
        decimal_places=3,
        help_text="Puntuación de confianza (0.0 - 1.0)"
    )
    
    processing_time = serializers.DecimalField(
        max_digits=8,
        decimal_places=3,
        help_text="Tiempo de procesamiento en segundos"
    )
    
    # URLs
    image_url = serializers.URLField(help_text="URL de la imagen original")
    
    # Métricas derivadas opcionales
    derived_metrics = serializers.DictField(
        required=False,
        help_text="Métricas calculadas adicionales (volumen, densidad, etc.)"
    )
    
    # Comparación de métodos (opcional)
    weight_comparison = serializers.DictField(
        required=False,
        help_text="Comparación entre métodos de predicción de peso"
    )


class CacaoImageListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listas de imágenes.
    
    Optimizado para rendimiento en listados con muchos elementos.
    """
    
    image_url = serializers.SerializerMethodField()
    quality_display = serializers.SerializerMethodField()
    
    class Meta:
        model = CacaoImage
        fields = [
            'id',
            'image_url',
            'width',
            'height', 
            'thickness',
            'weight',
            'predicted_quality',
            'quality_display',
            'quality_score',
            'batch_number',
            'is_processed',
            'processing_time',
            'created_at'
        ]
    
    def get_image_url(self, obj):
        """Obtiene la URL de la imagen."""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    def get_quality_display(self, obj):
        """Obtiene la descripción de calidad."""
        return obj.get_predicted_quality_display()


class PredictionStatsSerializer(serializers.Serializer):
    """
    Serializer para estadísticas de predicciones.
    """
    
    total_predictions = serializers.IntegerField()
    predictions_today = serializers.IntegerField()
    avg_processing_time = serializers.DecimalField(max_digits=8, decimal_places=3)
    
    quality_distribution = serializers.DictField()
    
    avg_dimensions = serializers.DictField()
    
    model_performance = serializers.DictField()


# Alias para compatibilidad
ImageSerializer = CacaoImageSerializer
