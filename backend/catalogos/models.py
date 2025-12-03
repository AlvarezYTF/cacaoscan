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
    codigo = models.CharField(max_length=20, unique=True, help_text="Código único del tema (ej: TIPO_DOC)")
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
    Tabla que almacena los parámetros o valores asociados a un tema.
    Ejemplo: Si el tema es "Tipo de Documento", los parámetros serían "CC", "CE", "PA", etc.
    """
    tema = models.ForeignKey(Tema, on_delete=models.CASCADE, related_name="parametros",
                            help_text="Tema al que pertenece este parámetro")
    codigo = models.CharField(max_length=20, help_text="Código del parámetro (ej: CC, M, F)")
    nombre = models.CharField(max_length=100, help_text="Nombre del parámetro (ej: Cédula de Ciudadanía)")
    descripcion = models.TextField(blank=True, default="", help_text="Descripción adicional del parámetro")
    activo = models.BooleanField(default=True, help_text="Indica si el parámetro está activo")

    class Meta:
        verbose_name = "Parámetro"
        verbose_name_plural = "Parámetros"
        ordering = ['tema', 'codigo']
        unique_together = ('tema', 'codigo')  # Un código único por tema
        indexes = [
            models.Index(fields=['tema', 'codigo']),
            models.Index(fields=['activo']),
        ]

    def __str__(self):
        return f"{self.tema.codigo} - {self.codigo}: {self.nombre}"

