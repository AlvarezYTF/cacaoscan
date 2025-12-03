# Generated manually - Add defaults to all nullable fields in ReporteGenerado
# -*- coding: utf-8 -*-
# This prevents Django from asking for one-off defaults when changing null=True to null=False

from django.db import migrations, models


def set_default_fields(apps, schema_editor):
    """Set default values for null values in fields."""
    ReporteGenerado = apps.get_model('reports', 'ReporteGenerado')
    
    # Update all nullable string fields to empty string
    ReporteGenerado.objects.filter(descripcion__isnull=True).update(descripcion="")
    ReporteGenerado.objects.filter(nombre_archivo__isnull=True).update(nombre_archivo="")
    ReporteGenerado.objects.filter(mensaje_error__isnull=True).update(mensaje_error="")
    # Update nullable integer field to 0
    ReporteGenerado.objects.filter(tamano_archivo__isnull=True).update(tamano_archivo=0)


def reverse_set_default_fields(apps, schema_editor):
    """Reverse migration - set null back."""
    ReporteGenerado = apps.get_model('reports', 'ReporteGenerado')
    
    # Reverse: set defaults back to null
    ReporteGenerado.objects.filter(descripcion="").update(descripcion=None)
    ReporteGenerado.objects.filter(nombre_archivo="").update(nombre_archivo=None)
    ReporteGenerado.objects.filter(mensaje_error="").update(mensaje_error=None)
    ReporteGenerado.objects.filter(tamano_archivo=0).update(tamano_archivo=None)


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0002_remove_reportegenerado_api_reporte_usuario_631114_idx_and_more'),
    ]

    operations = [
        # First, set default values for existing null records
        migrations.RunPython(
            set_default_fields,
            reverse_set_default_fields
        ),
        # Then, alter all fields to add defaults and remove null=True
        migrations.AlterField(
            model_name='reportegenerado',
            name='descripcion',
            field=models.TextField(
                blank=True,
                default=""
            ),
        ),
        migrations.AlterField(
            model_name='reportegenerado',
            name='nombre_archivo',
            field=models.CharField(
                blank=True,
                default="",
                max_length=255
            ),
        ),
        migrations.AlterField(
            model_name='reportegenerado',
            name='mensaje_error',
            field=models.TextField(
                blank=True,
                default=""
            ),
        ),
        migrations.AlterField(
            model_name='reportegenerado',
            name='tamano_archivo',
            field=models.PositiveIntegerField(
                blank=True,
                db_column='tamaño_archivo',
                default=0
            ),
        ),
    ]

