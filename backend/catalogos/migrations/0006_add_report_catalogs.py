# Generated migration for report catalogs (normalization)
# -*- coding: utf-8 -*-
from django.db import migrations, models


def create_initial_report_catalog_data(apps, schema_editor):
    """Create initial data for report catalogs."""
    TipoReporte = apps.get_model('catalogos', 'TipoReporte')
    FormatoReporte = apps.get_model('catalogos', 'FormatoReporte')
    EstadoReporte = apps.get_model('catalogos', 'EstadoReporte')
    
    # Create TipoReporte
    tipos_reporte = [
        {'codigo': 'CALIDAD', 'nombre': 'Reporte de Calidad', 'descripcion': 'Reporte de calidad de granos'},
        {'codigo': 'DEFECTOS', 'nombre': 'Reporte de Defectos', 'descripcion': 'Reporte de defectos detectados'},
        {'codigo': 'RENDIMIENTO', 'nombre': 'Reporte de Rendimiento', 'descripcion': 'Reporte de rendimiento de cultivos'},
        {'codigo': 'FINCA', 'nombre': 'Reporte de Finca', 'descripcion': 'Reporte de información de finca'},
        {'codigo': 'LOTE', 'nombre': 'Reporte de Lote', 'descripcion': 'Reporte de información de lote'},
        {'codigo': 'USUARIO', 'nombre': 'Reporte de Usuario', 'descripcion': 'Reporte de información de usuario'},
        {'codigo': 'AUDITORIA', 'nombre': 'Reporte de Auditoría', 'descripcion': 'Reporte de auditoría del sistema'},
        {'codigo': 'PERSONALIZADO', 'nombre': 'Reporte Personalizado', 'descripcion': 'Reporte personalizado'},
        {'codigo': 'ANALISIS_PERIODO', 'nombre': 'Análisis por Período', 'descripcion': 'Análisis de datos por período'},
    ]
    for tr in tipos_reporte:
        TipoReporte.objects.get_or_create(codigo=tr['codigo'], defaults=tr)
    
    # Create FormatoReporte
    formatos_reporte = [
        {'codigo': 'PDF', 'nombre': 'PDF', 'descripcion': 'Formato PDF'},
        {'codigo': 'EXCEL', 'nombre': 'Excel', 'descripcion': 'Formato Excel (.xlsx)'},
        {'codigo': 'CSV', 'nombre': 'CSV', 'descripcion': 'Formato CSV'},
        {'codigo': 'JSON', 'nombre': 'JSON', 'descripcion': 'Formato JSON'},
    ]
    for fr in formatos_reporte:
        FormatoReporte.objects.get_or_create(codigo=fr['codigo'], defaults=fr)
    
    # Create EstadoReporte
    estados_reporte = [
        {'codigo': 'PENDIENTE', 'nombre': 'Pendiente', 'descripcion': 'Reporte pendiente de generación'},
        {'codigo': 'GENERANDO', 'nombre': 'Generando', 'descripcion': 'Reporte en proceso de generación'},
        {'codigo': 'COMPLETADO', 'nombre': 'Completado', 'descripcion': 'Reporte generado exitosamente'},
        {'codigo': 'FALLIDO', 'nombre': 'Fallido', 'descripcion': 'Error al generar el reporte'},
        {'codigo': 'EXPIRADO', 'nombre': 'Expirado', 'descripcion': 'Reporte expirado'},
    ]
    for er in estados_reporte:
        EstadoReporte.objects.get_or_create(codigo=er['codigo'], defaults=er)


def reverse_create_initial_report_catalog_data(apps, schema_editor):
    """Reverse migration - delete catalog data."""
    TipoReporte = apps.get_model('catalogos', 'TipoReporte')
    FormatoReporte = apps.get_model('catalogos', 'FormatoReporte')
    EstadoReporte = apps.get_model('catalogos', 'EstadoReporte')
    
    TipoReporte.objects.all().delete()
    FormatoReporte.objects.all().delete()
    EstadoReporte.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('catalogos', '0005_rename_catalogos_clima_codigo_idx_catalogos_c_codigo_2169bb_idx_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TipoReporte',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(help_text='Código único del tipo de reporte', max_length=20, unique=True)),
                ('nombre', models.CharField(help_text='Nombre del tipo de reporte', max_length=100)),
                ('descripcion', models.TextField(blank=True, default='', help_text='Descripción del tipo de reporte')),
                ('activo', models.BooleanField(default=True, help_text='Indica si el tipo está activo')),
            ],
            options={
                'verbose_name': 'Tipo de Reporte',
                'verbose_name_plural': 'Tipos de Reporte',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='FormatoReporte',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(help_text='Código único del formato (ej: PDF, EXCEL)', max_length=20, unique=True)),
                ('nombre', models.CharField(help_text='Nombre del formato', max_length=100)),
                ('descripcion', models.TextField(blank=True, default='', help_text='Descripción del formato')),
                ('activo', models.BooleanField(default=True, help_text='Indica si el formato está activo')),
            ],
            options={
                'verbose_name': 'Formato de Reporte',
                'verbose_name_plural': 'Formatos de Reporte',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='EstadoReporte',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(help_text='Código único del estado (ej: PENDIENTE, COMPLETADO)', max_length=20, unique=True)),
                ('nombre', models.CharField(help_text='Nombre del estado', max_length=100)),
                ('descripcion', models.TextField(blank=True, default='', help_text='Descripción del estado')),
                ('activo', models.BooleanField(default=True, help_text='Indica si el estado está activo')),
            ],
            options={
                'verbose_name': 'Estado de Reporte',
                'verbose_name_plural': 'Estados de Reporte',
                'ordering': ['nombre'],
            },
        ),
        migrations.AddIndex(
            model_name='tiporeporte',
            index=models.Index(fields=['codigo'], name='catalogos_tiporeporte_codigo_idx'),
        ),
        migrations.AddIndex(
            model_name='tiporeporte',
            index=models.Index(fields=['activo'], name='catalogos_tiporeporte_activo_idx'),
        ),
        migrations.AddIndex(
            model_name='formatoreporte',
            index=models.Index(fields=['codigo'], name='catalogos_formatoreporte_codigo_idx'),
        ),
        migrations.AddIndex(
            model_name='formatoreporte',
            index=models.Index(fields=['activo'], name='catalogos_formatoreporte_activo_idx'),
        ),
        migrations.AddIndex(
            model_name='estadoreporte',
            index=models.Index(fields=['codigo'], name='catalogos_estadoreporte_codigo_idx'),
        ),
        migrations.AddIndex(
            model_name='estadoreporte',
            index=models.Index(fields=['activo'], name='catalogos_estadoreporte_activo_idx'),
        ),
        migrations.RunPython(
            create_initial_report_catalog_data,
            reverse_create_initial_report_catalog_data,
        ),
    ]

