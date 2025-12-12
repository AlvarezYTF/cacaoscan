from django.db import models
from core.models import TimeStampedModel


class Departamento(models.Model):
    """
    Tabla que almacena los departamentos de Colombia.
    Normalización 3FN: Cada departamento es único e independiente.
    """
    codigo = models.CharField(max_length=10, unique=True, help_text="Código del departamento (ej: 05 para Antioquia)")
    nombre = models.CharField(max_length=100, help_text="Nombre del departamento")

    class Meta:
        verbose_name = "Departamento"
        verbose_name_plural = "Departamentos"
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['nombre']),
        ]

    def __str__(self):
        return self.nombre

    @property
    def municipios_count(self):
        """Devuelve la cantidad de municipios del departamento."""
        return self.municipios.count()


class Municipio(models.Model):
    """
    Tabla que almacena los municipios de Colombia.
    Normalización 3FN: Cada municipio pertenece a un departamento (1:N).
    """
    departamento = models.ForeignKey(
        Departamento, 
        on_delete=models.CASCADE, 
        related_name="municipios",
        help_text="Departamento al que pertenece el municipio"
    )
    codigo = models.CharField(max_length=10, help_text="Código del municipio")
    nombre = models.CharField(max_length=100, help_text="Nombre del municipio")

    class Meta:
        verbose_name = "Municipio"
        verbose_name_plural = "Municipios"
        ordering = ['departamento', 'nombre']
        unique_together = ('departamento', 'codigo')  # Un código único por departamento
        indexes = [
            models.Index(fields=['departamento', 'codigo']),
            models.Index(fields=['nombre']),
        ]

    def __str__(self):
        return f"{self.nombre}, {self.departamento.nombre}"

class Tema(models.Model):
    """
    Tabla de catálogo que almacena las categorías generales del sistema.
    Ejemplos: Tipo de Documento, Sexo, Genética, etc.
    """
    codigo = models.CharField(max_length=30, unique=True, help_text="Código único del tema (ej: TIPO_DOC, TEMA_TIPO_NOTIFICACION)")
    nombre = models.CharField(max_length=100, help_text="Nombre del tema (ej: Tipo de Documento)")
    descripcion = models.TextField(blank=True, default="", help_text="Descripción del tema")
    activo = models.BooleanField(default=True, help_text="Indica si el tema está activo")

    class Meta:
        verbose_name = "Tema"
        verbose_name_plural = "Temas"
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['activo']),
        ]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    @property
    def parametros_count(self):
        """Devuelve la cantidad de parámetros activos del tema."""
        return self.parametros.filter(activo=True).count()


class Parametro(models.Model):
    """
    Tabla que almacena los parámetros o valores asociados a temas.
    Ejemplo: Si el tema es "Tipo de Documento", los parámetros serían "CC", "CE", "PA", etc.
    Cada parámetro pertenece a un solo tema (ForeignKey directo).
    """
    tema = models.ForeignKey(
        Tema,
        on_delete=models.CASCADE,
        related_name='parametros',
        help_text="Tema al que pertenece este parámetro"
    )
    codigo = models.CharField(max_length=20, help_text="Código del parámetro (ej: CC, M, F)")
    nombre = models.CharField(max_length=100, help_text="Nombre del parámetro (ej: Cédula de Ciudadanía)")
    descripcion = models.TextField(blank=True, default="", help_text="Descripción adicional del parámetro")
    activo = models.BooleanField(default=True, help_text="Indica si el parámetro está activo")
    metadata = models.JSONField(default=dict, blank=True, help_text="Metadata adicional para el parámetro (ej: mime_type para TipoArchivo, fecha_lanzamiento para VersionModelo)")

    class Meta:
        verbose_name = "Parámetro"
        verbose_name_plural = "Parámetros"
        ordering = ['tema', 'codigo']
        unique_together = ('tema', 'codigo')
        indexes = [
            models.Index(fields=['tema', 'codigo']),
            models.Index(fields=['activo']),
        ]

    def __str__(self):
        return f"{self.tema.codigo} - {self.codigo}: {self.nombre}"


class TemaParametro(models.Model):
    """
    Tabla pivot que relaciona Temas con Parámetros.
    Permite acceder a los IDs de la relación many-to-many.
    """
    tema = models.ForeignKey(
        Tema,
        on_delete=models.CASCADE,
        related_name='tema_parametro_set',
        help_text="Tema de la relación"
    )
    parametro = models.ForeignKey(
        Parametro,
        on_delete=models.CASCADE,
        related_name='tema_parametro_set',
        help_text="Parámetro de la relación"
    )

    class Meta:
        verbose_name = "Relación Tema-Parámetro"
        verbose_name_plural = "Relaciones Tema-Parámetro"
        unique_together = ('tema', 'parametro')
        indexes = [
            models.Index(fields=['tema', 'parametro']),
        ]

    def __str__(self):
        return f"{self.tema.codigo} - {self.parametro.codigo}"


class VariedadCacao(models.Model):
    """
    Catálogo de variedades de cacao.
    Normalización 3FN: Variedades centralizadas para evitar duplicación.
    """
    codigo = models.CharField(max_length=20, unique=True, help_text="Código único de la variedad (ej: CRIOLLO, FORASTERO)")
    nombre = models.CharField(max_length=100, help_text="Nombre de la variedad (ej: Criollo, Forastero, Trinitario)")
    descripcion = models.TextField(blank=True, default="", help_text="Descripción de la variedad")
    activo = models.BooleanField(default=True, help_text="Indica si la variedad está activa")
    
    class Meta:
        verbose_name = "Variedad de Cacao"
        verbose_name_plural = "Variedades de Cacao"
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['activo']),
        ]
    
    def __str__(self):
        return self.nombre


class TipoSuelo(models.Model):
    """
    Catálogo de tipos de suelo.
    Normalización 3FN: Tipos de suelo centralizados.
    """
    codigo = models.CharField(max_length=20, unique=True, help_text="Código único del tipo de suelo")
    nombre = models.CharField(max_length=100, help_text="Nombre del tipo de suelo")
    descripcion = models.TextField(blank=True, default="", help_text="Descripción del tipo de suelo")
    activo = models.BooleanField(default=True, help_text="Indica si el tipo está activo")
    
    class Meta:
        verbose_name = "Tipo de Suelo"
        verbose_name_plural = "Tipos de Suelo"
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['activo']),
        ]
    
    def __str__(self):
        return self.nombre


class Clima(models.Model):
    """
    Catálogo de tipos de clima.
    Normalización 3FN: Tipos de clima centralizados.
    """
    codigo = models.CharField(max_length=20, unique=True, help_text="Código único del tipo de clima")
    nombre = models.CharField(max_length=100, help_text="Nombre del tipo de clima")
    descripcion = models.TextField(blank=True, default="", help_text="Descripción del tipo de clima")
    activo = models.BooleanField(default=True, help_text="Indica si el tipo está activo")
    
    class Meta:
        verbose_name = "Clima"
        verbose_name_plural = "Climas"
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['activo']),
        ]
    
    def __str__(self):
        return self.nombre


class EstadoFinca(models.Model):
    """
    Catálogo de estados de finca.
    Normalización 3FN: Estados centralizados.
    """
    codigo = models.CharField(max_length=20, unique=True, help_text="Código único del estado (ej: ACTIVA, INACTIVA)")
    nombre = models.CharField(max_length=100, help_text="Nombre del estado")
    descripcion = models.TextField(blank=True, default="", help_text="Descripción del estado")
    activo = models.BooleanField(default=True, help_text="Indica si el estado está activo")
    
    class Meta:
        verbose_name = "Estado de Finca"
        verbose_name_plural = "Estados de Finca"
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['activo']),
        ]
    
    def __str__(self):
        return self.nombre


class EstadoLote(models.Model):
    """
    Catálogo de estados de lote.
    Normalización 3FN: Estados centralizados.
    """
    codigo = models.CharField(max_length=20, unique=True, help_text="Código único del estado (ej: ACTIVO, INACTIVO)")
    nombre = models.CharField(max_length=100, help_text="Nombre del estado")
    descripcion = models.TextField(blank=True, default="", help_text="Descripción del estado")
    activo = models.BooleanField(default=True, help_text="Indica si el estado está activo")
    
    class Meta:
        verbose_name = "Estado de Lote"
        verbose_name_plural = "Estados de Lote"
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['activo']),
        ]
    
    def __str__(self):
        return self.nombre


class TipoReporte(models.Model):
    """
    Catálogo de tipos de reporte.
    Normalización 3FN: Tipos centralizados para evitar duplicación.
    """
    codigo = models.CharField(max_length=20, unique=True, help_text="Código único del tipo de reporte")
    nombre = models.CharField(max_length=100, help_text="Nombre del tipo de reporte")
    descripcion = models.TextField(blank=True, default="", help_text="Descripción del tipo de reporte")
    activo = models.BooleanField(default=True, help_text="Indica si el tipo está activo")
    
    class Meta:
        verbose_name = "Tipo de Reporte"
        verbose_name_plural = "Tipos de Reporte"
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['activo']),
        ]
    
    def __str__(self):
        return self.nombre


class FormatoReporte(models.Model):
    """
    Catálogo de formatos de reporte.
    Normalización 3FN: Formatos centralizados.
    """
    codigo = models.CharField(max_length=20, unique=True, help_text="Código único del formato (ej: PDF, EXCEL)")
    nombre = models.CharField(max_length=100, help_text="Nombre del formato")
    descripcion = models.TextField(blank=True, default="", help_text="Descripción del formato")
    activo = models.BooleanField(default=True, help_text="Indica si el formato está activo")
    
    class Meta:
        verbose_name = "Formato de Reporte"
        verbose_name_plural = "Formatos de Reporte"
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['activo']),
        ]
    
    def __str__(self):
        return self.nombre


class EstadoReporte(models.Model):
    """
    Catálogo de estados de reporte.
    Normalización 3FN: Estados centralizados.
    """
    codigo = models.CharField(max_length=20, unique=True, help_text="Código único del estado (ej: PENDIENTE, COMPLETADO)")
    nombre = models.CharField(max_length=100, help_text="Nombre del estado")
    descripcion = models.TextField(blank=True, default="", help_text="Descripción del estado")
    activo = models.BooleanField(default=True, help_text="Indica si el estado está activo")
    
    class Meta:
        verbose_name = "Estado de Reporte"
        verbose_name_plural = "Estados de Reporte"
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['activo']),
        ]
    
    def __str__(self):
        return self.nombre


class TipoNotificacion(models.Model):
    """
    Catálogo de tipos de notificación.
    Normalización 3FN: Tipos centralizados para evitar duplicación.
    """
    codigo = models.CharField(max_length=20, unique=True, help_text="Código único del tipo (ej: INFO, WARNING, ERROR, SUCCESS)")
    nombre = models.CharField(max_length=100, help_text="Nombre del tipo de notificación")
    descripcion = models.TextField(blank=True, default="", help_text="Descripción del tipo")
    activo = models.BooleanField(default=True, help_text="Indica si el tipo está activo")
    
    class Meta:
        verbose_name = "Tipo de Notificación"
        verbose_name_plural = "Tipos de Notificación"
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['activo']),
        ]
    
    def __str__(self):
        return self.nombre


class TipoArchivo(models.Model):
    """
    Catálogo de tipos de archivo.
    Normalización 1NF/3NF: Tipos centralizados para evitar duplicación de valores.
    """
    codigo = models.CharField(max_length=50, unique=True, help_text="Código único del tipo (ej: IMAGE_JPEG, IMAGE_PNG, IMAGE_WEBP)")
    nombre = models.CharField(max_length=100, help_text="Nombre del tipo de archivo (ej: JPEG, PNG, WebP)")
    mime_type = models.CharField(max_length=100, help_text="MIME type del archivo (ej: image/jpeg, image/png)")
    descripcion = models.TextField(blank=True, default="", help_text="Descripción del tipo de archivo")
    activo = models.BooleanField(default=True, help_text="Indica si el tipo está activo")
    
    class Meta:
        verbose_name = "Tipo de Archivo"
        verbose_name_plural = "Tipos de Archivo"
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['mime_type']),
            models.Index(fields=['activo']),
        ]
    
    def __str__(self):
        return self.nombre


class TipoDispositivo(models.Model):
    """
    Catálogo de tipos de dispositivos para procesamiento ML.
    Normalización 3NF: Dispositivos centralizados para evitar duplicación.
    """
    codigo = models.CharField(max_length=20, unique=True, help_text="Código único del dispositivo (ej: CPU, CUDA, MPS)")
    nombre = models.CharField(max_length=100, help_text="Nombre del dispositivo (ej: CPU, GPU CUDA, Apple Silicon)")
    descripcion = models.TextField(blank=True, default="", help_text="Descripción del dispositivo")
    activo = models.BooleanField(default=True, help_text="Indica si el dispositivo está activo")
    
    class Meta:
        verbose_name = "Tipo de Dispositivo"
        verbose_name_plural = "Tipos de Dispositivo"
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['activo']),
        ]
    
    def __str__(self):
        return self.nombre


class VersionModelo(models.Model):
    """
    Catálogo de versiones de modelos ML.
    Normalización 3NF: Versiones centralizadas para evitar duplicación.
    """
    codigo = models.CharField(max_length=50, unique=True, help_text="Código único de la versión (ej: v1.0, v2.0, v1.5)")
    nombre = models.CharField(max_length=100, help_text="Nombre de la versión (ej: v1.0, v2.0)")
    descripcion = models.TextField(blank=True, default="", help_text="Descripción de la versión del modelo")
    fecha_lanzamiento = models.DateField(null=True, blank=True, help_text="Fecha de lanzamiento de la versión")
    activo = models.BooleanField(default=True, help_text="Indica si la versión está activa")
    
    class Meta:
        verbose_name = "Versión de Modelo"
        verbose_name_plural = "Versiones de Modelo"
        ordering = ['-codigo']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['activo']),
        ]
    
    def __str__(self):
        return self.nombre