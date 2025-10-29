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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cacao_images')
    
    # Archivo de imagen
    image = models.ImageField(upload_to='cacao_images/processed/%Y/%m/%d/')
    
    # Metadatos de procesamiento
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    
    # Metadatos del grano/finca
    finca = models.CharField(max_length=200, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    lote = models.ForeignKey(
        'fincas_app.Lote', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='cacao_images',
        help_text="Lote al que pertenece esta imagen"
    )
    variedad = models.CharField(max_length=100, blank=True, null=True)
    fecha_cosecha = models.DateField(blank=True, null=True)
    notas = models.TextField(blank=True, null=True)
    
    # Información técnica del archivo
    file_name = models.CharField(max_length=255, blank=True, null=True)
    file_size = models.PositiveIntegerField(blank=True, null=True)
    file_type = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        verbose_name = 'Imagen de Cacao'
        verbose_name_plural = 'Imágenes de Cacao'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['processed']),
            models.Index(fields=['region', 'finca']),
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


class CacaoPrediction(models.Model):
    """
    Modelo para almacenar resultados de predicciones ML de granos de cacao.
    """
    image = models.OneToOneField(CacaoImage, on_delete=models.CASCADE, related_name='prediction')
    
    # Predicciones de dimensiones (en mm)
    alto_mm = models.DecimalField(max_digits=8, decimal_places=2)
    ancho_mm = models.DecimalField(max_digits=8, decimal_places=2)
    grosor_mm = models.DecimalField(max_digits=8, decimal_places=2)
    peso_g = models.DecimalField(max_digits=8, decimal_places=2)
    
    # Scores de confianza (0.0 a 1.0)
    confidence_alto = models.DecimalField(max_digits=4, decimal_places=3, default=0.0)
    confidence_ancho = models.DecimalField(max_digits=4, decimal_places=3, default=0.0)
    confidence_grosor = models.DecimalField(max_digits=4, decimal_places=3, default=0.0)
    confidence_peso = models.DecimalField(max_digits=4, decimal_places=3, default=0.0)
    
    # Metadatos de procesamiento
    processing_time_ms = models.PositiveIntegerField(help_text="Tiempo de procesamiento en milisegundos")
    crop_url = models.URLField(max_length=500, blank=True, null=True, help_text="URL del crop procesado")
    
    # Información técnica del modelo
    model_version = models.CharField(max_length=50, default='v1.0')
    device_used = models.CharField(max_length=20, default='cpu', choices=[
        ('cpu', 'CPU'),
        ('cuda', 'GPU CUDA'),
        ('mps', 'Apple Silicon'),
    ])
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Predicción de Cacao'
        verbose_name_plural = 'Predicciones de Cacao'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['image']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['model_version']),
        ]
    
    def __str__(self):
        return f"Predicción {self.id} - {self.image.user.username} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
    
    @property
    def average_confidence(self):
        """Calcular confianza promedio."""
        from django.utils import timezone
        confidences = [
            float(self.confidence_alto),
            float(self.confidence_ancho),
            float(self.confidence_grosor),
            float(self.confidence_peso)
        ]
        return round(sum(confidences) / len(confidences), 3)
    
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
