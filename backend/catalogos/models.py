from django.db import models
from core.models import TimeStampedModel


class Departamento(models.Model):
    """
    Tabla que almacena los departamentos de Colombia.
    NormalizaciÃ³n 3FN: Cada departamento es Ãºnico e independiente.
    """
    codigo = models.CharField(max_length=10, unique=True, help_text="CÃ³digo del departamento (ej: 05 para Antioquia)")
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
    NormalizaciÃ³n 3FN: Cada municipio pertenece a un departamento (1:N).
    """
    departamento = models.ForeignKey(
        Departamento, 
        on_delete=models.CASCADE, 
        related_name="municipios",
        help_text="Departamento al que pertenece el municipio"
    )
    codigo = models.CharField(max_length=10, help_text="CÃ³digo del municipio")
    nombre = models.CharField(max_length=100, help_text="Nombre del municipio")

    class Meta:
        verbose_name = "Municipio"
        verbose_name_plural = "Municipios"
        ordering = ['departamento', 'nombre']
        unique_together = ('departamento', 'codigo')  # Un cÃ³digo Ãºnico por departamento
        indexes = [
            models.Index(fields=['departamento', 'codigo']),
            models.Index(fields=['nombre']),
        ]

    def __str__(self):
        return f"{self.nombre}, {self.departamento.nombre}"

class Tema(models.Model):
    """
    Tabla de catÃ¡logo que almacena las categorÃ­as generales del sistema.
    Ejemplos: Tipo de Documento, Sexo, GenÃ©tica, etc.
    """
    codigo = models.CharField(max_length=20, unique=True, help_text="CÃ³digo Ãºnico del tema (ej: TIPO_DOC)")
    nombre = models.CharField(max_length=100, help_text="Nombre del tema (ej: Tipo de Documento)")
    descripcion = models.TextField(null=True, blank=True, help_text="DescripciÃ³n del tema")
    activo = models.BooleanField(default=True, help_text="Indica si el tema estÃ¡ activo")

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
        """Devuelve la cantidad de parÃ¡metros activos del tema."""
        return self.parametros.filter(activo=True).count()


class Parametro(models.Model):
    """
    Tabla que almacena los parÃ¡metros o valores asociados a un tema.
    Ejemplo: Si el tema es "Tipo de Documento", los parÃ¡metros serÃ­an "CC", "CE", "PA", etc.
    """
    tema = models.ForeignKey(Tema, on_delete=models.CASCADE, related_name="parametros",
                            help_text="Tema al que pertenece este parÃ¡metro")
    codigo = models.CharField(max_length=20, help_text="CÃ³digo del parÃ¡metro (ej: CC, M, F)")
    nombre = models.CharField(max_length=100, help_text="Nombre del parÃ¡metro (ej: CÃ©dula de CiudadanÃ­a)")
    descripcion = models.TextField(null=True, blank=True, help_text="DescripciÃ³n adicional del parÃ¡metro")
    activo = models.BooleanField(default=True, help_text="Indica si el parÃ¡metro estÃ¡ activo")

    class Meta:
        verbose_name = "ParÃ¡metro"
        verbose_name_plural = "ParÃ¡metros"
        ordering = ['tema', 'codigo']
        unique_together = ('tema', 'codigo')  # Un cÃ³digo Ãºnico por tema
        indexes = [
            models.Index(fields=['tema', 'codigo']),
            models.Index(fields=['activo']),
        ]

    def __str__(self):
        return f"{self.tema.codigo} - {self.codigo}: {self.nombre}"

