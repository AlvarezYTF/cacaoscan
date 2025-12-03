# Generated manually - Add nombre field and additional fields to Lote model
# -*- coding: utf-8 -*-

from django.db import migrations, models


def set_lote_nombre_from_identificador(apps, schema_editor):
    """Set nombre from identificador for existing lotes."""
    Lote = apps.get_model('fincas_app', 'Lote')
    for lote in Lote.objects.all():
        if not lote.nombre:
            lote.nombre = lote.identificador if lote.identificador else f'Lote {lote.id}'
            lote.save(update_fields=['nombre'])


def reverse_set_lote_nombre(apps, schema_editor):
    """Reverse migration - no action needed."""
    pass


def populate_fecha_fields_from_timestamps(apps, schema_editor):
    """Populate fecha_creacion and fecha_actualizacion from created_at and updated_at."""
    Lote = apps.get_model('fincas_app', 'Lote')
    for lote in Lote.objects.all():
        if hasattr(lote, 'created_at') and lote.created_at:
            lote.fecha_creacion = lote.created_at
        if hasattr(lote, 'updated_at') and lote.updated_at:
            lote.fecha_actualizacion = lote.updated_at
        lote.save(update_fields=['fecha_creacion', 'fecha_actualizacion'])


def reverse_populate_fecha_fields(apps, schema_editor):
    """Reverse migration - no action needed."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('fincas_app', '0007_add_finca_additional_fields'),
    ]

    operations = [
        # First add nombre as nullable with default
        migrations.AddField(
            model_name='lote',
            name='nombre',
            field=models.CharField(default='Lote', help_text='Nombre del lote', max_length=200, null=True, blank=True),
        ),
        # Set nombre from identificador for existing records
        migrations.RunPython(
            set_lote_nombre_from_identificador,
            reverse_set_lote_nombre
        ),
        # Make nombre required (remove null and blank)
        migrations.AlterField(
            model_name='lote',
            name='nombre',
            field=models.CharField(help_text='Nombre del lote', max_length=200),
        ),
        migrations.AddField(
            model_name='lote',
            name='edad_plantas',
            field=models.PositiveIntegerField(blank=True, help_text='Edad de las plantas en meses', null=True),
        ),
        # Add fecha_creacion and fecha_actualizacion as nullable first
        migrations.AddField(
            model_name='lote',
            name='fecha_creacion',
            field=models.DateTimeField(help_text='Fecha de creación del lote', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='lote',
            name='fecha_actualizacion',
            field=models.DateTimeField(help_text='Fecha de última actualización', null=True, blank=True),
        ),
        # Populate fecha fields from created_at and updated_at
        migrations.RunPython(
            populate_fecha_fields_from_timestamps,
            reverse_populate_fecha_fields
        ),
        # Make fecha_creacion and fecha_actualizacion use auto_now_add and auto_now
        migrations.AlterField(
            model_name='lote',
            name='fecha_creacion',
            field=models.DateTimeField(auto_now_add=True, help_text='Fecha de creación del lote'),
        ),
        migrations.AlterField(
            model_name='lote',
            name='fecha_actualizacion',
            field=models.DateTimeField(auto_now=True, help_text='Fecha de última actualización'),
        ),
    ]

