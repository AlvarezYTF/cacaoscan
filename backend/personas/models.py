"""
Modelos para gestión de personas - App personas.
Modelos normalizados según Tercera Forma Normal (3FN).
"""
from django.db import models
from django.contrib.auth.models import User


class TipoDocumento(models.Model):
    """Modelo para tipos de documento de identidad."""
    codigo = models.CharField(max_length=5, unique=True, help_text="Código del tipo de documento")
    nombre = models.CharField(max_length=50, help_text="Nombre del tipo de documento")
    
    class Meta:
        verbose_name = 'Tipo de Documento'
        verbose_name_plural = 'Tipos de Documento'
        ordering = ['codigo']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Genero(models.Model):
    """Modelo para géneros."""
    codigo = models.CharField(max_length=5, unique=True, help_text="Código del género")
    nombre = models.CharField(max_length=30, help_text="Nombre del género")
    
    class Meta:
        verbose_name = 'Género'
        verbose_name_plural = 'Géneros'
        ordering = ['codigo']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Ubicacion(models.Model):
    """Modelo para ubicaciones geográficas."""
    municipio = models.CharField(max_length=100, help_text="Municipio")
    departamento = models.CharField(max_length=100, help_text="Departamento")
    
    class Meta:
        verbose_name = 'Ubicación'
        verbose_name_plural = 'Ubicaciones'
        unique_together = ['municipio', 'departamento']
        ordering = ['departamento', 'municipio']
    
    def __str__(self):
        return f"{self.municipio}, {self.departamento}"


class Persona(models.Model):
    """Modelo para información personal complementaria del usuario."""
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name="persona",
        help_text="Usuario asociado a la persona"
    )
    tipo_documento = models.ForeignKey(
        TipoDocumento, 
        on_delete=models.PROTECT,
        help_text="Tipo de documento de identidad"
    )
    numero_documento = models.CharField(
        max_length=20, 
        unique=True,
        help_text="Número de documento de identidad"
    )
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
    telefono = models.CharField(max_length=15, help_text="Número de teléfono")
    direccion = models.CharField(
        max_length=255, 
        null=True, 
        blank=True,
        help_text="Dirección de residencia"
    )
    genero = models.ForeignKey(
        Genero, 
        on_delete=models.PROTECT,
        help_text="Género"
    )
    fecha_nacimiento = models.DateField(
        null=True, 
        blank=True,
        help_text="Fecha de nacimiento"
    )
    ubicacion = models.ForeignKey(
        Ubicacion, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Ubicación geográfica"
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
