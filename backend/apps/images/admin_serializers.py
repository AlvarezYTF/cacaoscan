"""
Serializers administrativos para la gestión de datos de imágenes de cacao.

Proporciona serialización y validación para endpoints administrativos
con permisos especiales para CRUD completo y operaciones avanzadas.
"""

import os
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import CacaoImage


class AdminCacaoImageSerializer(serializers.ModelSerializer):
    """
    Serializer administrativo para CRUD completo del modelo CacaoImage.
    
    Permite editar todos los campos, incluyendo las predicciones ML,
    con validaciones específicas para administradores.
    """
    
    # URLs calculadas
    image_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    
    # Campos calculados de solo lectura
    file_size_display = serializers.SerializerMethodField()
    aspect_ratio = serializers.SerializerMethodField()
    volume_estimate = serializers.SerializerMethodField()
    density_estimate = serializers.SerializerMethodField()
    quality_display = serializers.SerializerMethodField()
    
    # Validaciones personalizadas para campos críticos
    width = serializers.DecimalField(
        max_digits=8,
        decimal_places=3,
        validators=[
            MinValueValidator(Decimal('0.001')),
            MaxValueValidator(Decimal('100.000'))
        ],
        required=False,
        allow_null=True,
        help_text="Ancho del grano en milímetros (0.001 - 100.000)"
    )
    
    height = serializers.DecimalField(
        max_digits=8,
        decimal_places=3,
        validators=[
            MinValueValidator(Decimal('0.001')),
            MaxValueValidator(Decimal('100.000'))
        ],
        required=False,
        allow_null=True,
        help_text="Alto del grano en milímetros (0.001 - 100.000)"
    )
    
    thickness = serializers.DecimalField(
        max_digits=8,
        decimal_places=3,
        validators=[
            MinValueValidator(Decimal('0.001')),
            MaxValueValidator(Decimal('100.000'))
        ],
        required=False,
        allow_null=True,
        help_text="Grosor del grano en milímetros (0.001 - 100.000)"
    )
    
    weight = serializers.DecimalField(
        max_digits=8,
        decimal_places=4,
        validators=[
            MinValueValidator(Decimal('0.0001')),
            MaxValueValidator(Decimal('50.0000'))
        ],
        required=False,
        allow_null=True,
        help_text="Peso del grano en gramos (0.0001 - 50.0000)"
    )
    
    quality_score = serializers.DecimalField(
        max_digits=5,
        decimal_places=3,
        validators=[
            MinValueValidator(Decimal('0.000')),
            MaxValueValidator(Decimal('1.000'))
        ],
        required=False,
        allow_null=True,
        help_text="Puntuación de calidad (0.000 - 1.000)"
    )
    
    processing_time = serializers.DecimalField(
        max_digits=8,
        decimal_places=3,
        validators=[
            MinValueValidator(Decimal('0.000')),
            MaxValueValidator(Decimal('300.000'))
        ],
        required=False,
        allow_null=True,
        help_text="Tiempo de procesamiento en segundos (0.000 - 300.000)"
    )
    
    class Meta:
        model = CacaoImage
        fields = [
            # Identificación
            'id',
            'image',
            'image_url',
            'thumbnail_url',
            
            # Características físicas (editables por admin)
            'width',
            'height',
            'thickness',
            'weight',
            
            # Información de calidad (editables por admin)
            'quality_score',
            'predicted_quality',
            'quality_display',
            'defect_type',
            'defect_confidence',
            
            # Metadatos de imagen (solo lectura)
            'image_width',
            'image_height',
            'file_size',
            'file_size_display',
            
            # Estados de procesamiento (editables por admin)
            'is_processed',
            'processing_time',
            
            # Información adicional (editables)
            'batch_number',
            'origin',
            'harvest_date',
            'notes',
            'uploaded_by',
            
            # Campos calculados (solo lectura)
            'aspect_ratio',
            'volume_estimate',
            'density_estimate',
            
            # Timestamps (solo lectura)
            'created_at',
            'updated_at'
        ]
        
        read_only_fields = [
            'id',
            'image_width',
            'image_height',
            'file_size',
            'file_size_display',
            'aspect_ratio',
            'volume_estimate',
            'density_estimate',
            'quality_display',
            'image_url',
            'thumbnail_url',
            'created_at',
            'updated_at'
        ]
    
    def get_image_url(self, obj):
        """Obtiene la URL completa de la imagen."""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    def get_thumbnail_url(self, obj):
        """Obtiene la URL del thumbnail (placeholder por ahora)."""
        # TODO: Implementar generación de thumbnails
        return self.get_image_url(obj)
    
    def get_file_size_display(self, obj):
        """Obtiene el tamaño del archivo en formato legible."""
        return obj.get_file_size_display()
    
    def get_aspect_ratio(self, obj):
        """Calcula la relación de aspecto."""
        return obj.aspect_ratio
    
    def get_volume_estimate(self, obj):
        """Obtiene la estimación de volumen."""
        return obj.volume_estimate
    
    def get_density_estimate(self, obj):
        """Obtiene la estimación de densidad."""
        return obj.density_estimate
    
    def get_quality_display(self, obj):
        """Obtiene la descripción de calidad."""
        return obj.get_quality_display_with_score()
    
    def validate(self, attrs):
        """
        Validaciones a nivel de objeto.
        
        Args:
            attrs: Atributos validados
            
        Returns:
            dict: Atributos validados
            
        Raises:
            serializers.ValidationError: Si hay errores de validación
        """
        # Validar consistencia de dimensiones
        width = attrs.get('width')
        height = attrs.get('height')
        thickness = attrs.get('thickness')
        weight = attrs.get('weight')
        
        # Si se proporcionan dimensiones, validar proporciones realistas
        if width and height and thickness:
            # Verificar que las proporciones sean realistas para granos de cacao
            if width < height * 0.5 or width > height * 3.0:
                raise serializers.ValidationError({
                    'width': 'La relación ancho/alto debe estar entre 0.5 y 3.0 para granos de cacao'
                })
            
            if thickness > min(width, height):
                raise serializers.ValidationError({
                    'thickness': 'El grosor no puede ser mayor que el ancho o alto'
                })
            
            # Si también se proporciona peso, verificar densidad razonable
            if weight:
                volume = (4/3) * 3.14159 * (width/2) * (height/2) * (thickness/2)
                density = float(weight) / (float(volume) / 1000)  # g/cm³
                
                if density < 0.3 or density > 2.0:
                    raise serializers.ValidationError({
                        'weight': f'La densidad calculada ({density:.2f} g/cm³) está fuera del rango esperado para granos de cacao (0.3-2.0 g/cm³)'
                    })
        
        # Validar que quality_score esté alineado con predicted_quality
        quality_score = attrs.get('quality_score')
        predicted_quality = attrs.get('predicted_quality')
        
        if quality_score is not None and predicted_quality:
            expected_ranges = {
                'excellent': (0.8, 1.0),
                'good': (0.6, 0.8),
                'fair': (0.4, 0.6),
                'poor': (0.0, 0.4)
            }
            
            if predicted_quality in expected_ranges:
                min_score, max_score = expected_ranges[predicted_quality]
                if not (min_score <= float(quality_score) <= max_score):
                    raise serializers.ValidationError({
                        'quality_score': f'La puntuación ({quality_score}) no coincide con la calidad predicha ({predicted_quality}). Rango esperado: {min_score}-{max_score}'
                    })
        
        return attrs
    
    def update(self, instance, validated_data):
        """
        Actualiza una instancia existente con logging de cambios.
        
        Args:
            instance: Instancia existente
            validated_data: Datos validados
            
        Returns:
            CacaoImage: Instancia actualizada
        """
        # Registrar cambios importantes
        important_fields = ['width', 'height', 'thickness', 'weight', 'quality_score']
        changes = []
        
        for field in important_fields:
            if field in validated_data:
                old_value = getattr(instance, field)
                new_value = validated_data[field]
                
                if old_value != new_value:
                    changes.append(f"{field}: {old_value} → {new_value}")
        
        # Actualizar instancia
        instance = super().update(instance, validated_data)
        
        # Log cambios si los hay
        if changes:
            import logging
            logger = logging.getLogger('admin')
            user = self.context.get('request').user if self.context.get('request') else 'Unknown'
            logger.info(f"Admin {user} actualizó imagen {instance.id}: {', '.join(changes)}")
        
        return instance


class AdminImageBulkUpdateSerializer(serializers.Serializer):
    """
    Serializer para actualización masiva de imágenes.
    
    Permite aplicar cambios a múltiples registros simultáneamente.
    """
    
    image_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        min_length=1,
        max_length=100,
        help_text="Lista de IDs de imágenes a actualizar (máximo 100)"
    )
    
    # Campos opcionales para actualización masiva
    batch_number = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        help_text="Nuevo número de lote para todas las imágenes"
    )
    
    origin = serializers.CharField(
        max_length=200,
        required=False,
        allow_blank=True,
        help_text="Nueva origen para todas las imágenes"
    )
    
    predicted_quality = serializers.ChoiceField(
        choices=CacaoImage.QUALITY_CHOICES,
        required=False,
        help_text="Nueva calidad predicha para todas las imágenes"
    )
    
    defect_type = serializers.ChoiceField(
        choices=CacaoImage.DEFECT_CHOICES,
        required=False,
        help_text="Nuevo tipo de defecto para todas las imágenes"
    )
    
    notes = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        help_text="Notas adicionales para todas las imágenes"
    )
    
    def validate_image_ids(self, value):
        """Valida que todas las IDs existan."""
        existing_ids = set(CacaoImage.objects.filter(id__in=value).values_list('id', flat=True))
        missing_ids = set(value) - existing_ids
        
        if missing_ids:
            raise serializers.ValidationError(f"Las siguientes IDs no existen: {sorted(missing_ids)}")
        
        return value
    
    def validate(self, attrs):
        """Valida que al menos un campo de actualización esté presente."""
        update_fields = ['batch_number', 'origin', 'predicted_quality', 'defect_type', 'notes']
        
        if not any(field in attrs for field in update_fields):
            raise serializers.ValidationError(
                "Debe proporcionar al menos un campo para actualizar"
            )
        
        return attrs


class TrainingJobSerializer(serializers.Serializer):
    """
    Serializer para trabajos de entrenamiento de modelos ML.
    
    Valida parámetros para el reentrenamiento de modelos.
    """
    
    # Parámetros de entrenamiento
    model_type = serializers.ChoiceField(
        choices=[('regression', 'Regresión'), ('vision', 'Visión')],
        help_text="Tipo de modelo a entrenar"
    )
    
    epochs = serializers.IntegerField(
        min_value=1,
        max_value=1000,
        default=100,
        help_text="Número de épocas de entrenamiento (1-1000)"
    )
    
    learning_rate = serializers.DecimalField(
        max_digits=6,
        decimal_places=5,
        min_value=Decimal('0.00001'),
        max_value=Decimal('1.00000'),
        default=Decimal('0.001'),
        help_text="Tasa de aprendizaje (0.00001-1.00000)"
    )
    
    batch_size = serializers.IntegerField(
        min_value=1,
        max_value=128,
        default=32,
        help_text="Tamaño del lote (1-128)"
    )
    
    validation_split = serializers.DecimalField(
        max_digits=3,
        decimal_places=2,
        min_value=Decimal('0.10'),
        max_value=Decimal('0.50'),
        default=Decimal('0.20'),
        help_text="Porcentaje de datos para validación (0.10-0.50)"
    )
    
    # Filtros de datos
    min_quality_score = serializers.DecimalField(
        max_digits=5,
        decimal_places=3,
        min_value=Decimal('0.000'),
        max_value=Decimal('1.000'),
        required=False,
        help_text="Puntuación mínima de calidad para incluir en entrenamiento"
    )
    
    exclude_defective = serializers.BooleanField(
        default=False,
        help_text="Excluir granos con defectos del entrenamiento"
    )
    
    only_processed = serializers.BooleanField(
        default=True,
        help_text="Solo usar imágenes procesadas para entrenamiento"
    )
    
    # Opciones avanzadas
    save_intermediate = serializers.BooleanField(
        default=True,
        help_text="Guardar modelos intermedios durante el entrenamiento"
    )
    
    notify_completion = serializers.BooleanField(
        default=True,
        help_text="Enviar notificación al completar el entrenamiento"
    )
    
    def validate(self, attrs):
        """Validaciones específicas según el tipo de modelo."""
        model_type = attrs['model_type']
        
        # Validaciones específicas para modelo de visión
        if model_type == 'vision':
            if attrs['batch_size'] > 64:
                raise serializers.ValidationError({
                    'batch_size': 'Para modelos de visión, el tamaño de lote no debe exceder 64'
                })
            
            if attrs['learning_rate'] > Decimal('0.01'):
                raise serializers.ValidationError({
                    'learning_rate': 'Para modelos de visión, la tasa de aprendizaje no debe exceder 0.01'
                })
        
        # Validaciones específicas para modelo de regresión
        elif model_type == 'regression':
            if attrs['epochs'] > 500:
                raise serializers.ValidationError({
                    'epochs': 'Para modelos de regresión, no se recomiendan más de 500 épocas'
                })
        
        return attrs


class TrainingJobStatusSerializer(serializers.Serializer):
    """
    Serializer para el estado de trabajos de entrenamiento.
    
    Proporciona información sobre el progreso y resultados.
    """
    
    job_id = serializers.CharField(help_text="ID único del trabajo")
    model_type = serializers.CharField(help_text="Tipo de modelo")
    status = serializers.ChoiceField(
        choices=[
            ('pending', 'Pendiente'),
            ('running', 'Ejecutándose'),
            ('completed', 'Completado'),
            ('failed', 'Fallido'),
            ('cancelled', 'Cancelado')
        ],
        help_text="Estado actual del trabajo"
    )
    
    progress = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        min_value=Decimal('0.00'),
        max_value=Decimal('100.00'),
        help_text="Progreso del entrenamiento (0.00-100.00%)"
    )
    
    current_epoch = serializers.IntegerField(
        min_value=0,
        help_text="Época actual del entrenamiento"
    )
    
    total_epochs = serializers.IntegerField(
        min_value=1,
        help_text="Total de épocas programadas"
    )
    
    # Métricas actuales
    current_loss = serializers.DecimalField(
        max_digits=10,
        decimal_places=6,
        required=False,
        help_text="Pérdida actual del modelo"
    )
    
    current_accuracy = serializers.DecimalField(
        max_digits=5,
        decimal_places=3,
        required=False,
        help_text="Precisión actual del modelo"
    )
    
    validation_loss = serializers.DecimalField(
        max_digits=10,
        decimal_places=6,
        required=False,
        help_text="Pérdida de validación actual"
    )
    
    validation_accuracy = serializers.DecimalField(
        max_digits=5,
        decimal_places=3,
        required=False,
        help_text="Precisión de validación actual"
    )
    
    # Información temporal
    started_at = serializers.DateTimeField(
        required=False,
        help_text="Momento de inicio del entrenamiento"
    )
    
    estimated_completion = serializers.DateTimeField(
        required=False,
        help_text="Tiempo estimado de finalización"
    )
    
    completed_at = serializers.DateTimeField(
        required=False,
        help_text="Momento de finalización"
    )
    
    # Información adicional
    dataset_size = serializers.IntegerField(
        min_value=0,
        help_text="Número de muestras en el dataset de entrenamiento"
    )
    
    validation_size = serializers.IntegerField(
        min_value=0,
        help_text="Número de muestras en el dataset de validación"
    )
    
    error_message = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Mensaje de error si el entrenamiento falló"
    )
    
    log_url = serializers.URLField(
        required=False,
        help_text="URL para descargar logs del entrenamiento"
    )


class AdminStatsSerializer(serializers.Serializer):
    """
    Serializer para estadísticas administrativas detalladas.
    
    Proporciona métricas avanzadas para administradores.
    """
    
    # Estadísticas generales
    total_images = serializers.IntegerField()
    processed_images = serializers.IntegerField()
    unprocessed_images = serializers.IntegerField()
    
    # Estadísticas de calidad
    quality_distribution = serializers.DictField()
    defect_distribution = serializers.DictField()
    
    # Estadísticas de dimensiones
    dimension_statistics = serializers.DictField()
    
    # Estadísticas temporales
    images_by_month = serializers.DictField()
    processing_times = serializers.DictField()
    
    # Estadísticas de modelos ML
    model_performance = serializers.DictField()
    
    # Estadísticas de almacenamiento
    storage_usage = serializers.DictField()
    
    # Estadísticas de usuarios
    user_activity = serializers.DictField()
