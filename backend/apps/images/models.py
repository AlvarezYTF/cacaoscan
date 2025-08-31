"""
Modelos para la gestión de imágenes de granos de cacao.

Este módulo contiene los modelos de base de datos para almacenar
información sobre las imágenes de granos de cacao y sus características físicas.
"""

import os
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from PIL import Image as PILImage


def upload_cacao_image(instance, filename):
    """
    Función para generar la ruta de subida de imágenes de cacao.
    
    Args:
        instance: Instancia del modelo CacaoImage
        filename: Nombre original del archivo
        
    Returns:
        str: Ruta donde se guardará el archivo
    """
    # Obtener la extensión del archivo
    ext = filename.split('.')[-1]
    
    # Generar un nombre único usando UUID
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    
    # Crear la ruta: cacao_images/YYYY/MM/DD/filename
    from datetime import datetime
    now = datetime.now()
    date_path = f"{now.year}/{now.month:02d}/{now.day:02d}"
    
    return f"cacao_images/{date_path}/{unique_filename}"


class CacaoImage(models.Model):
    """
    Modelo para almacenar imágenes de granos de cacao y sus características físicas.
    
    Este modelo permite registrar imágenes de granos de cacao junto con
    mediciones físicas detalladas para análisis posterior.
    """
    
    # Opciones para el estado de calidad del grano
    QUALITY_CHOICES = [
        ('excellent', 'Excelente'),
        ('good', 'Bueno'),
        ('fair', 'Regular'),
        ('poor', 'Deficiente'),
        ('unknown', 'Desconocido'),
    ]
    
    # Opciones para el tipo de defecto (si aplica)
    DEFECT_CHOICES = [
        ('none', 'Sin defecto'),
        ('mold', 'Moho'),
        ('insect_damage', 'Daño por insectos'),
        ('broken', 'Roto'),
        ('germinated', 'Germinado'),
        ('flat', 'Plano'),
        ('purple', 'Púrpura'),
        ('slaty', 'Pizarroso'),
        ('other', 'Otro'),
    ]
    
    # Información básica de la imagen
    image = models.ImageField(
        upload_to=upload_cacao_image,
        verbose_name="Imagen del grano",
        help_text="Imagen del grano de cacao para análisis"
    )
    
    # Características físicas del grano (mediciones en mm y gramos)
    width = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        validators=[MinValueValidator(0.001)],
        verbose_name="Ancho (mm)",
        help_text="Ancho del grano en milímetros",
        null=True,
        blank=True
    )
    
    height = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        validators=[MinValueValidator(0.001)],
        verbose_name="Alto (mm)",
        help_text="Alto del grano en milímetros",
        null=True,
        blank=True
    )
    
    thickness = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        validators=[MinValueValidator(0.001)],
        verbose_name="Grosor (mm)",
        help_text="Grosor del grano en milímetros",
        null=True,
        blank=True
    )
    
    weight = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        validators=[MinValueValidator(0.0001)],
        verbose_name="Peso (g)",
        help_text="Peso del grano en gramos",
        null=True,
        blank=True
    )
    
    # Información de calidad y clasificación
    quality_score = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="Puntuación de calidad",
        help_text="Puntuación de calidad calculada por ML (0.0 - 1.0)",
        null=True,
        blank=True
    )
    
    predicted_quality = models.CharField(
        max_length=20,
        choices=QUALITY_CHOICES,
        default='unknown',
        verbose_name="Calidad predicha",
        help_text="Calidad predicha por el modelo de ML"
    )
    
    defect_type = models.CharField(
        max_length=20,
        choices=DEFECT_CHOICES,
        default='none',
        verbose_name="Tipo de defecto",
        help_text="Tipo de defecto detectado en el grano"
    )
    
    defect_confidence = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="Confianza del defecto",
        help_text="Nivel de confianza en la detección del defecto (0.0 - 1.0)",
        null=True,
        blank=True
    )
    
    # Metadatos de la imagen
    image_width = models.PositiveIntegerField(
        verbose_name="Ancho de imagen (px)",
        help_text="Ancho de la imagen en píxeles",
        null=True,
        blank=True
    )
    
    image_height = models.PositiveIntegerField(
        verbose_name="Alto de imagen (px)",
        help_text="Alto de la imagen en píxeles",
        null=True,
        blank=True
    )
    
    file_size = models.PositiveIntegerField(
        verbose_name="Tamaño del archivo (bytes)",
        help_text="Tamaño del archivo de imagen en bytes",
        null=True,
        blank=True
    )
    
    # Información de procesamiento
    is_processed = models.BooleanField(
        default=False,
        verbose_name="Procesada",
        help_text="Indica si la imagen ha sido procesada por ML"
    )
    
    processing_time = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        verbose_name="Tiempo de procesamiento (s)",
        help_text="Tiempo que tomó procesar la imagen en segundos",
        null=True,
        blank=True
    )
    
    # Información del usuario y timestamps
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Subido por",
        help_text="Usuario que subió la imagen"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación",
        help_text="Fecha y hora de creación del registro"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de actualización",
        help_text="Fecha y hora de la última actualización"
    )
    
    # Campos adicionales para análisis
    notes = models.TextField(
        blank=True,
        verbose_name="Notas",
        help_text="Notas adicionales sobre el grano"
    )
    
    batch_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Número de lote",
        help_text="Número de lote al que pertenece el grano"
    )
    
    origin = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Origen",
        help_text="Origen geográfico del grano"
    )
    
    harvest_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de cosecha",
        help_text="Fecha de cosecha del grano"
    )
    
    class Meta:
        verbose_name = "Imagen de Cacao"
        verbose_name_plural = "Imágenes de Cacao"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['predicted_quality']),
            models.Index(fields=['defect_type']),
            models.Index(fields=['batch_number']),
            models.Index(fields=['is_processed']),
        ]
    
    def __str__(self):
        """Representación en string del modelo."""
        if self.batch_number:
            return f"Grano {self.id} - Lote {self.batch_number} ({self.predicted_quality})"
        return f"Grano {self.id} - {self.predicted_quality}"
    
    def save(self, *args, **kwargs):
        """Sobrescribe el método save para extraer metadatos de la imagen."""
        # Llamar al save original primero
        super().save(*args, **kwargs)
        
        # Extraer metadatos de la imagen si existe
        if self.image and not self.image_width:
            try:
                with PILImage.open(self.image.path) as img:
                    self.image_width = img.width
                    self.image_height = img.height
                
                # Obtener tamaño del archivo
                self.file_size = os.path.getsize(self.image.path)
                
                # Guardar los metadatos (sin crear un bucle infinito)
                CacaoImage.objects.filter(pk=self.pk).update(
                    image_width=self.image_width,
                    image_height=self.image_height,
                    file_size=self.file_size
                )
            except Exception as e:
                # Log del error si es necesario, pero no fallar el save
                pass
    
    @property
    def aspect_ratio(self):
        """Calcula la relación de aspecto del grano."""
        if self.width and self.height:
            return float(self.width) / float(self.height)
        return None
    
    @property
    def volume_estimate(self):
        """Estima el volumen del grano (aproximación elipsoidal)."""
        if self.width and self.height and self.thickness:
            # Aproximación: V = (4/3) * π * a * b * c
            # donde a, b, c son los semi-ejes
            import math
            a = float(self.width) / 2
            b = float(self.height) / 2
            c = float(self.thickness) / 2
            return (4/3) * math.pi * a * b * c
        return None
    
    @property
    def density_estimate(self):
        """Estima la densidad del grano."""
        volume = self.volume_estimate
        if volume and self.weight:
            return float(self.weight) / volume
        return None
    
    def get_quality_display_with_score(self):
        """Devuelve la calidad con la puntuación si está disponible."""
        quality_display = self.get_predicted_quality_display()
        if self.quality_score:
            return f"{quality_display} ({self.quality_score:.3f})"
        return quality_display
    
    def is_defective(self):
        """Determina si el grano tiene algún defecto."""
        return self.defect_type != 'none'
    
    def get_file_size_display(self):
        """Devuelve el tamaño del archivo en formato legible."""
        if not self.file_size:
            return "Desconocido"
        
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"


class CacaoImageAnalysis(models.Model):
    """
    Modelo para almacenar análisis detallados de las imágenes de cacao.
    
    Este modelo permite guardar múltiples análisis de la misma imagen
    con diferentes modelos o parámetros.
    """
    
    image = models.ForeignKey(
        CacaoImage,
        on_delete=models.CASCADE,
        related_name='analyses',
        verbose_name="Imagen",
        help_text="Imagen de cacao analizada"
    )
    
    model_name = models.CharField(
        max_length=100,
        verbose_name="Nombre del modelo",
        help_text="Nombre del modelo ML utilizado para el análisis"
    )
    
    model_version = models.CharField(
        max_length=50,
        verbose_name="Versión del modelo",
        help_text="Versión del modelo ML utilizado"
    )
    
    confidence_scores = models.JSONField(
        default=dict,
        verbose_name="Puntuaciones de confianza",
        help_text="Puntuaciones de confianza para cada clase"
    )
    
    feature_vector = models.JSONField(
        default=list,
        verbose_name="Vector de características",
        help_text="Vector de características extraído por el modelo"
    )
    
    processing_metadata = models.JSONField(
        default=dict,
        verbose_name="Metadatos de procesamiento",
        help_text="Información adicional sobre el procesamiento"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de análisis",
        help_text="Fecha y hora del análisis"
    )
    
    class Meta:
        verbose_name = "Análisis de Imagen"
        verbose_name_plural = "Análisis de Imágenes"
        ordering = ['-created_at']
        unique_together = ['image', 'model_name', 'model_version']
        indexes = [
            models.Index(fields=['model_name']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        """Representación en string del modelo."""
        return f"Análisis {self.model_name} v{self.model_version} - Imagen {self.image.id}"
