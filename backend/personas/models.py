"""
Modelos para gestión de personas - App personas.
Modelos normalizados según Tercera Forma Normal (3FN).

INTEGRACI"N CON M"DULOS:
- Catálogos (Tema-Parámetro): Para tipo_documento y genero
- Ubicaciones: Para departamento y municipio
"""
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
import re
from catalogos.models import Parametro, Departamento, Municipio


class Persona(models.Model):
    """
    Modelo para información personal complementaria del usuario.
    
    INTEGRACI"N CON CATLOGOS:
    - tipo_documento: Se relaciona con Parametro donde tema__codigo='TIPO_DOC'
    - genero: Se relaciona con Parametro donde tema__codigo='SEXO'
    
    INTEGRACI"N CON UBICACIONES:
    - departamento: Se relaciona con Departamento (relación 1:N)
    - municipio: Se relaciona con Municipio (relación 1:N)
    
    NORMALIZACI"N 3FN: Mantiene integridad referencial con catálogos y ubicaciones normalizadas.
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name="persona",
        help_text="Usuario asociado a la persona"
    )
    
    # CATLOGO: Tipo de documento (Parametro del tema TIPO_DOC)
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
        blank=True,
        default="",
        help_text="Segundo nombre (opcional)"
    )
    primer_apellido = models.CharField(max_length=50, help_text="Primer apellido")
    segundo_apellido = models.CharField(
        max_length=50, 
        blank=True,
        default="",
        help_text="Segundo apellido (opcional)"
    )
    
    # Contacto
    telefono = models.CharField(
        max_length=15, 
        unique=True,
        help_text="Número de teléfono (único)"
    )
    direccion = models.CharField(
        max_length=255, 
        blank=True,
        default="",
        help_text="Dirección de residencia"
    )
    
    # CATLOGO: Género (Parametro del tema SEXO)
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
    
    # UBICACI"N: Departamento y Municipio normalizados
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
        indexes = [
            models.Index(fields=['numero_documento']),
            models.Index(fields=['telefono']),
            models.Index(fields=['user']),
        ]
    
    def _validate_document_number(self, errors):
        """Validate document number."""
        if not self.numero_documento:
            return
        
        if not self.numero_documento.isdigit():
            errors['numero_documento'] = 'El número de documento solo puede contener números.'
        elif len(self.numero_documento) < 6 or len(self.numero_documento) > 11:
            errors['numero_documento'] = 'El número de documento debe tener entre 6 y 11 dígitos.'
    
    def _validate_phone(self, errors):
        """Validate phone number."""
        if not self.telefono:
            return
        
        cleaned_phone = re.sub(r'[\s\-\(\)]', '', self.telefono)
        if cleaned_phone.startswith('+'):
            cleaned_phone = cleaned_phone[1:]
        
        if not cleaned_phone.isdigit():
            errors['telefono'] = 'El teléfono solo puede contener números.'
        elif len(cleaned_phone) < 7 or len(cleaned_phone) > 15:
            errors['telefono'] = 'El teléfono debe tener entre 7 y 15 dígitos.'
    
    def _validate_birth_date(self, errors):
        """Validate birth date."""
        if not self.fecha_nacimiento:
            return
        
        hoy = timezone.now().date()
        if self.fecha_nacimiento > hoy:
            errors['fecha_nacimiento'] = 'La fecha de nacimiento no puede ser futura.'
            return
        
        edad = hoy.year - self.fecha_nacimiento.year - \
               ((hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
        
        if edad < 14:
            errors['fecha_nacimiento'] = 'La persona debe tener al menos 14 años.'
        if edad > 120:
            errors['fecha_nacimiento'] = 'La fecha de nacimiento no es válida.'
    
    def _validate_names(self, errors):
        """Validate name fields."""
        if self.primer_nombre and not all(char.isalpha() or char.isspace() for char in self.primer_nombre):
            errors['primer_nombre'] = 'El primer nombre solo puede contener letras.'
        
        if self.primer_apellido and not all(char.isalpha() or char.isspace() for char in self.primer_apellido):
            errors['primer_apellido'] = 'El primer apellido solo puede contener letras.'
    
    def _validate_municipality_department(self, errors):
        """Validate municipality belongs to department."""
        if self.municipio and self.departamento:
            if self.municipio.departamento != self.departamento:
                errors['municipio'] = 'El municipio no pertenece al departamento seleccionado.'
    
    def clean(self):
        """Validaciones personalizadas a nivel de modelo."""
        errors = {}
        
        self._validate_document_number(errors)
        self._validate_phone(errors)
        self._validate_birth_date(errors)
        self._validate_names(errors)
        self._validate_municipality_department(errors)
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        """Sobrescribir save para ejecutar validaciones."""
        self.full_clean()  # Ejecuta clean() y otras validaciones
        super().save(*args, **kwargs)
    
    def __str__(self):
        nombre_completo = f"{self.primer_nombre}"
        if self.segundo_nombre:
            nombre_completo += f" {self.segundo_nombre}"
        nombre_completo += f" {self.primer_apellido}"
        if self.segundo_apellido:
            nombre_completo += f" {self.segundo_apellido}"
        return nombre_completo

    @property
    def nombre_completo(self):
        """Devuelve el nombre completo de la persona."""
        return str(self)
    
    @property
    def edad(self):
        """Calcula la edad actual de la persona."""
        if not self.fecha_nacimiento:
            return None
        hoy = timezone.now().date()
        return hoy.year - self.fecha_nacimiento.year - \
               ((hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))


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


