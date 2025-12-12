"""
Modelos para imágenes y predicciones en CacaoScan.
"""
from django.db import models
from django.contrib.auth.models import User
from core.models import TimeStampedModel


class CacaoImage(TimeStampedModel):
    """
    Modelo para almacenar imágenes de granos de cacao procesadas.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='images_app_cacao_images')
    
    # Archivo de imagen
    image = models.ImageField(upload_to='dataset/')
    
    # Metadatos de procesamiento
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    
    # Metadatos del grano/finca
    # NOTA: finca se elimina por 2NF - se obtiene a través de lote.finca
    lote = models.ForeignKey(
        'fincas_app.Lote', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='cacao_images',
        help_text="Lote al que pertenece esta imagen (la finca se obtiene de lote.finca)"
    )
    notas = models.TextField(blank=True, default="")
    
    # Información técnica del archivo
    file_name = models.CharField(max_length=255, blank=True, default="")
    file_size = models.PositiveIntegerField(blank=True, null=True)
    file_type = models.ForeignKey(
        'catalogos.Parametro',
        on_delete=models.PROTECT,
        related_name='cacao_images',
        null=True,
        blank=True,
        limit_choices_to={'tema__codigo': 'TEMA_TIPO_ARCHIVO'},
        help_text="Tipo de archivo (normalizado)"
    )
    
    # Metadata adicional (JSONB) para contexto y datos flexibles
    metadata = models.JSONField(
        blank=True, 
        default=dict, 
        help_text="Metadata adicional en formato JSON. Evitar duplicar datos que deberían ser ForeignKeys o campos normalizados. Usar solo para datos verdaderamente flexibles y no estructurados."
    )
    
    class Meta:
        verbose_name = 'Imagen de Cacao'
        verbose_name_plural = 'Imágenes de Cacao'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['processed']),
            models.Index(fields=['lote']),
        ]
    
    def __str__(self):
        return f"Imagen {self.id} - {self.user.username} ({self.uploaded_at.strftime('%Y-%m-%d')})"
    
    @property
    def file_size_mb(self):
        """Obtener tamaño del archivo en MB."""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return None
    
    @property
    def has_prediction(self):
        """Verificar si tiene predicción asociada."""
        return hasattr(self, 'prediction') and self.prediction is not None
    
    @property
    def filename(self):
        """Obtener nombre del archivo (compatibilidad con tests)."""
        if self.file_name:
            return self.file_name
        if self.image:
            return self.image.name
        return ""
    
    @property
    def finca(self):
        """Obtener finca a través de lote (normalización 2NF - eliminada redundancia)."""
        if self.lote and self.lote.finca:
            return self.lote.finca
        return None
    
    def clean(self):
        """
        Validar que metadata no contenga datos que deberían ser ForeignKeys o campos normalizados.
        """
        from django.core.exceptions import ValidationError
        
        if self.metadata:
            # Validar que no contenga objetos completos de entidades normalizadas
            forbidden_keys = ['finca', 'municipio', 'departamento', 'variedad', 'lote', 'usuario', 'file_type']
            for key in forbidden_keys:
                if key in self.metadata and isinstance(self.metadata[key], dict):
                    # Si contiene un objeto completo, debe ser solo un ID
                    if 'id' not in self.metadata[key] and len(self.metadata[key]) > 1:
                        raise ValidationError({
                            'metadata': f'metadata no debe contener objetos completos de {key}. Usar solo el ID (ej: {{"{key}_id": 123}}) o eliminar si ya existe como ForeignKey'
                        })
    
    def save(self, *args, **kwargs):
        """Override save to call clean validation."""
        self.full_clean()
        super().save(*args, **kwargs)


class CacaoPrediction(models.Model):
    """
    Modelo para almacenar resultados de predicciones ML de granos de cacao.
    """
    image = models.OneToOneField(CacaoImage, on_delete=models.CASCADE, related_name='prediction')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='predictions', null=True, blank=True, help_text="Usuario que realizó la predicción")
    
    # Predicciones de dimensiones (en mm)
    alto_mm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    ancho_mm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    grosor_mm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    peso_g = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Scores de confianza (0.0 a 1.0)
    confidence_alto = models.DecimalField(max_digits=4, decimal_places=3, default=0.0)
    confidence_ancho = models.DecimalField(max_digits=4, decimal_places=3, default=0.0)
    confidence_grosor = models.DecimalField(max_digits=4, decimal_places=3, default=0.0)
    confidence_peso = models.DecimalField(max_digits=4, decimal_places=3, default=0.0)
    
    # Campos adicionales requeridos por tests
    quality_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Puntuación de calidad")
    maturity_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Porcentaje de madurez")
    defects_count = models.PositiveIntegerField(default=0, help_text="Número de defectos detectados")
    analysis_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pendiente'),
            ('processing', 'Procesando'),
            ('completed', 'Completado'),
            ('failed', 'Fallido'),
        ],
        default='pending',
        help_text="Estado del análisis"
    )
    processing_time = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Tiempo de procesamiento en segundos")
    
    # Metadatos de procesamiento
    processing_time_ms = models.PositiveIntegerField(null=True, blank=True, help_text="Tiempo de procesamiento en milisegundos")
    crop_url = models.URLField(max_length=500, blank=True, null=True, help_text="URL del crop procesado")
    
    # Información técnica del modelo (normalizado 3NF)
    model_version = models.ForeignKey(
        'catalogos.Parametro',
        on_delete=models.PROTECT,
        related_name='predictions_model_version',
        limit_choices_to={'tema__codigo': 'TEMA_VERSION_MODELO'},
        help_text="Versión del modelo usado (normalizado)"
    )
    device_used = models.ForeignKey(
        'catalogos.Parametro',
        on_delete=models.PROTECT,
        related_name='predictions_device_used',
        limit_choices_to={'tema__codigo': 'TEMA_TIPO_DISPOSITIVO'},
        help_text="Dispositivo usado para procesamiento (normalizado)"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Alias para compatibilidad con tests
    @property
    def created(self):
        """Alias para created_at (compatibilidad con tests)."""
        return self.created_at
    
    @created.setter
    def created(self, value):
        """Setter para created (compatibilidad con tests)."""
        self.created_at = value
    
    class Meta:
        verbose_name = 'Predicción de Cacao'
        verbose_name_plural = 'Predicciones de Cacao'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['image']),
            models.Index(fields=['-created_at']),
            # Note: Django automatically creates indexes for ForeignKeys (model_version, device_used)
        ]
    
    def __str__(self):
        """Representación string de la predicción."""
        filename = self.image.filename if hasattr(self.image, 'filename') else f"Imagen {self.image.id}"
        quality = f"{self.quality_score}" if self.quality_score else "N/A"
        return f"Predicción para {filename} - Calidad: {quality}"
    
    @property
    def average_confidence(self):
        """Calcular confianza promedio."""
        confidences = []
        if self.confidence_alto is not None:
            try:
                confidences.append(float(self.confidence_alto))
            except (TypeError, ValueError):
                pass
        if self.confidence_ancho is not None:
            try:
                confidences.append(float(self.confidence_ancho))
            except (TypeError, ValueError):
                pass
        if self.confidence_grosor is not None:
            try:
                confidences.append(float(self.confidence_grosor))
            except (TypeError, ValueError):
                pass
        if self.confidence_peso is not None:
            try:
                confidences.append(float(self.confidence_peso))
            except (TypeError, ValueError):
                pass
        
        if confidences:
            return round(sum(confidences) / len(confidences), 3)
        return 0.0
    
    @property
    def volume_cm3(self):
        """Calcular volumen aproximado en cm³."""
        import math
        a = float(self.alto_mm) / 10
        b = float(self.ancho_mm) / 10
        c = float(self.grosor_mm) / 10
        volume = (4/3) * math.pi * a * b * c
        return round(volume, 3)
    
    @property
    def density_g_cm3(self):
        """Calcular densidad aproximada en g/cm³."""
        if self.volume_cm3 > 0:
            density = float(self.peso_g) / self.volume_cm3
            return round(density, 3)
        return None


