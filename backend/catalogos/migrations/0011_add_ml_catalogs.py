# Generated migration to add ML-related catalogs (3NF normalization)
# -*- coding: utf-8 -*-
from django.db import migrations, models


def create_default_tipos_dispositivo(apps, schema_editor):
    """Create default device types."""
    TipoDispositivo = apps.get_model('catalogos', 'TipoDispositivo')
    
    tipos = [
        ('CPU', 'CPU', 'Procesador central (CPU)'),
        ('CUDA', 'GPU CUDA', 'Unidad de procesamiento gráfico con CUDA'),
        ('MPS', 'Apple Silicon', 'Apple Silicon (Metal Performance Shaders)'),
    ]
    
    for codigo, nombre, descripcion in tipos:
        TipoDispositivo.objects.get_or_create(
            codigo=codigo,
            defaults={
                'nombre': nombre,
                'descripcion': descripcion,
                'activo': True
            }
        )


def create_default_versiones_modelo(apps, schema_editor):
    """Create default model versions."""
    VersionModelo = apps.get_model('catalogos', 'VersionModelo')
    
    versiones = [
        ('v1.0', 'v1.0', 'Versión inicial del modelo'),
        ('v1.5', 'v1.5', 'Versión mejorada del modelo'),
        ('v2.0', 'v2.0', 'Segunda versión del modelo'),
    ]
    
    for codigo, nombre, descripcion in versiones:
        VersionModelo.objects.get_or_create(
            codigo=codigo,
            defaults={
                'nombre': nombre,
                'descripcion': descripcion,
                'activo': True
            }
        )


def reverse_create_defaults(apps, schema_editor):
    """Reverse migration - delete all tipos."""
    TipoDispositivo = apps.get_model('catalogos', 'TipoDispositivo')
    VersionModelo = apps.get_model('catalogos', 'VersionModelo')
    TipoDispositivo.objects.all().delete()
    VersionModelo.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('catalogos', '0010_add_tipo_archivo'),
    ]

    operations = [
        migrations.CreateModel(
            name='TipoDispositivo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(help_text='Código único del dispositivo (ej: CPU, CUDA, MPS)', max_length=20, unique=True)),
                ('nombre', models.CharField(help_text='Nombre del dispositivo (ej: CPU, GPU CUDA, Apple Silicon)', max_length=100)),
                ('descripcion', models.TextField(blank=True, default='', help_text='Descripción del dispositivo')),
                ('activo', models.BooleanField(default=True, help_text='Indica si el dispositivo está activo')),
            ],
            options={
                'verbose_name': 'Tipo de Dispositivo',
                'verbose_name_plural': 'Tipos de Dispositivo',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='VersionModelo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(help_text='Código único de la versión (ej: v1.0, v2.0, v1.5)', max_length=50, unique=True)),
                ('nombre', models.CharField(help_text='Nombre de la versión (ej: v1.0, v2.0)', max_length=100)),
                ('descripcion', models.TextField(blank=True, default='', help_text='Descripción de la versión del modelo')),
                ('fecha_lanzamiento', models.DateField(blank=True, help_text='Fecha de lanzamiento de la versión', null=True)),
                ('activo', models.BooleanField(default=True, help_text='Indica si la versión está activa')),
            ],
            options={
                'verbose_name': 'Versión de Modelo',
                'verbose_name_plural': 'Versiones de Modelo',
                'ordering': ['-codigo'],
            },
        ),
        migrations.AddIndex(
            model_name='tipodispositivo',
            index=models.Index(fields=['codigo'], name='catalogos_t_codigo_disp_idx'),
        ),
        migrations.AddIndex(
            model_name='tipodispositivo',
            index=models.Index(fields=['activo'], name='catalogos_t_activo_disp_idx'),
        ),
        migrations.AddIndex(
            model_name='versionmodelo',
            index=models.Index(fields=['codigo'], name='catalogos_v_codigo_vers_idx'),
        ),
        migrations.AddIndex(
            model_name='versionmodelo',
            index=models.Index(fields=['activo'], name='catalogos_v_activo_vers_idx'),
        ),
        migrations.RunPython(
            create_default_tipos_dispositivo,
            reverse_create_defaults,
        ),
        migrations.RunPython(
            create_default_versiones_modelo,
            reverse_create_defaults,
        ),
    ]

