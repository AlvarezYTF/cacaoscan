# Generated migration to add TipoNotificacion catalog (3NF normalization)
# -*- coding: utf-8 -*-
from django.db import migrations, models


def create_default_tipos_notificacion(apps, schema_editor):
    """Create default notification types."""
    TipoNotificacion = apps.get_model('catalogos', 'TipoNotificacion')
    
    tipos = [
        ('INFO', 'Información', 'Notificación informativa'),
        ('WARNING', 'Advertencia', 'Notificación de advertencia'),
        ('ERROR', 'Error', 'Notificación de error'),
        ('SUCCESS', 'Éxito', 'Notificación de éxito'),
        ('DEFECT_ALERT', 'Alerta de Defecto', 'Alerta sobre defectos detectados'),
        ('REPORT_READY', 'Reporte Listo', 'Notificación de reporte completado'),
        ('TRAINING_COMPLETE', 'Entrenamiento Completo', 'Notificación de entrenamiento completado'),
        ('WELCOME', 'Bienvenida', 'Notificación de bienvenida'),
    ]
    
    for codigo, nombre, descripcion in tipos:
        TipoNotificacion.objects.get_or_create(
            codigo=codigo,
            defaults={
                'nombre': nombre,
                'descripcion': descripcion,
                'activo': True
            }
        )


def reverse_create_default_tipos_notificacion(apps, schema_editor):
    """Reverse migration - delete all tipos."""
    TipoNotificacion = apps.get_model('catalogos', 'TipoNotificacion')
    TipoNotificacion.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('catalogos', '0007_rename_catalogos_estadoreporte_codigo_idx_catalogos_e_codigo_45aae3_idx_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TipoNotificacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(help_text='Código único del tipo (ej: INFO, WARNING, ERROR, SUCCESS)', max_length=20, unique=True)),
                ('nombre', models.CharField(help_text='Nombre del tipo de notificación', max_length=100)),
                ('descripcion', models.TextField(blank=True, default='', help_text='Descripción del tipo')),
                ('activo', models.BooleanField(default=True, help_text='Indica si el tipo está activo')),
            ],
            options={
                'verbose_name': 'Tipo de Notificación',
                'verbose_name_plural': 'Tipos de Notificación',
                'ordering': ['nombre'],
            },
        ),
        migrations.AddIndex(
            model_name='tiponotificacion',
            index=models.Index(fields=['codigo'], name='catalogos_t_codigo_8a1b2c_idx'),
        ),
        migrations.AddIndex(
            model_name='tiponotificacion',
            index=models.Index(fields=['activo'], name='catalogos_t_activo_3d4e5f_idx'),
        ),
        migrations.RunPython(
            create_default_tipos_notificacion,
            reverse_create_default_tipos_notificacion,
        ),
    ]

