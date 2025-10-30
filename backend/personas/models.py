"""
Modelos para gestión de personas - App personas.
Modelos normalizados según Tercera Forma Normal (3FN).

INTEGRACIÓN CON MÓDULOS:
- Catálogos (Tema-Parámetro): Para tipo_documento y genero
- Ubicaciones: Para departamento y municipio
"""
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from catalogos.models import Parametro, Departamento, Municipio


class Persona(models.Model):
    """
    Modelo para información personal complementaria del usuario.
    
    INTEGRACIÓN CON CATÁLOGOS:
    - tipo_documento: Se relaciona con Parametro donde tema__codigo='TIPO_DOC'
    - genero: Se relaciona con Parametro donde tema__codigo='SEXO'
    
    INTEGRACIÓN CON UBICACIONES:
    - departamento: Se relaciona con Departamento (relación 1:N)
    - municipio: Se relaciona con Municipio (relación 1:N)
    
    NORMALIZACIÓN 3FN: Mantiene integridad referencial con catálogos y ubicaciones normalizadas.
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name="persona",
        help_text="Usuario asociado a la persona"
    )
    
    # CATÁLOGO: Tipo de documento (Parametro del tema TIPO_DOC)
    tipo_documento = models.ForeignKey(
        Parametro, 
        on_delete=models.PROTECT,
        limit_choices_to={'tema__codigo': 'TIPO_DOC'},
        related_name="personas_tipo_doc",
        help_text="Parámetro del catálogo TIPO_DOC (ej: CC, CE, PA, TI, RC)"
    )
    
    numero_documento = models.CharField(
        max_length=20, 
        unique=True,
        help_text="Número de documento de identidad"
    )
    
    # Información personal
    primer_nombre = models.CharField(max_length=50, help_text="Primer nombre")
    segundo_nombre = models.CharField(
        max_length=50, 
        null=True, 
        blank=True,
        help_text="Segundo nombre (opcional)"
    )
    primer_apellido = models.CharField(max_length=50, help_text="Primer apellido")
    segundo_apellido = models.CharField(
        max_length=50, 
        null=True, 
        blank=True,
        help_text="Segundo apellido (opcional)"
    )
    
    # Contacto
    telefono = models.CharField(max_length=15, help_text="Número de teléfono")
    direccion = models.CharField(
        max_length=255, 
        null=True, 
        blank=True,
        help_text="Dirección de residencia"
    )
    
    # CATÁLOGO: Género (Parametro del tema SEXO)
    genero = models.ForeignKey(
        Parametro, 
        on_delete=models.PROTECT,
        limit_choices_to={'tema__codigo': 'SEXO'},
        related_name="personas_genero",
        help_text="Parámetro del catálogo SEXO (ej: M, F, O)"
    )
    
    # Ubicación geográfica (normalizada)
    fecha_nacimiento = models.DateField(
        null=True, 
        blank=True,
        help_text="Fecha de nacimiento"
    )
    
    # UBICACIÓN: Departamento y Municipio normalizados
    departamento = models.ForeignKey(
        Departamento, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="personas",
        help_text="Departamento de residencia"
    )
    municipio = models.ForeignKey(
        Municipio, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="personas",
        help_text="Municipio de residencia"
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True, help_text="Fecha de creación del registro")
    
    class Meta:
        verbose_name = 'Persona'
        verbose_name_plural = 'Personas'
        ordering = ['primer_apellido', 'primer_nombre']
    
    def __str__(self):
        nombre_completo = f"{self.primer_nombre}"
        if self.segundo_nombre:
            nombre_completo += f" {self.segundo_nombre}"
        nombre_completo += f" {self.primer_apellido}"
        if self.segundo_apellido:
            nombre_completo += f" {self.segundo_apellido}"
        return nombre_completo


class PendingRegistration(models.Model):
    """
    Modelo para almacenar registros pendientes de verificación de correo.
    Los datos del usuario no se crean hasta que el correo esté verificado.
    """
    email = models.EmailField(unique=True, help_text="Email del usuario pendiente de registro")
    data = models.JSONField(help_text="Datos del formulario de registro en formato JSON")
    verification_token = models.UUIDField(default=uuid.uuid4, unique=True, help_text="Token único de verificación")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Fecha y hora de creación del registro pendiente")
    is_verified = models.BooleanField(default=False, help_text="Indica si el correo ya fue verificado")
    verified_at = models.DateTimeField(null=True, blank=True, help_text="Fecha y hora de verificación")
    
    class Meta:
        verbose_name = 'Registro Pendiente'
        verbose_name_plural = 'Registros Pendientes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['verification_token']),
            models.Index(fields=['is_verified', 'created_at']),
        ]
    
    def __str__(self):
        return f"Registro pendiente: {self.email}"
    
    def is_expired(self):
        """Verifica si el token de verificación ha expirado (más de 24 horas)."""
        expiration_time = self.created_at + timedelta(hours=24)
        return timezone.now() > expiration_time
    
    def verify(self):
        """Marca el registro como verificado."""
        self.is_verified = True
        self.verified_at = timezone.now()
        self.save()
