# Generated migration for normalization catalogs
# -*- coding: utf-8 -*-
from django.db import migrations, models, connection


def create_initial_catalog_data(apps, schema_editor):
    """Create initial data for normalization catalogs."""
    VariedadCacao = apps.get_model('catalogos', 'VariedadCacao')
    TipoSuelo = apps.get_model('catalogos', 'TipoSuelo')
    Clima = apps.get_model('catalogos', 'Clima')
    EstadoFinca = apps.get_model('catalogos', 'EstadoFinca')
    EstadoLote = apps.get_model('catalogos', 'EstadoLote')
    
    # Create VariedadCacao
    variedades = [
        {'codigo': 'CRIOLLO', 'nombre': 'Criollo', 'descripcion': 'Variedad de cacao criollo'},
        {'codigo': 'FORASTERO', 'nombre': 'Forastero', 'descripcion': 'Variedad de cacao forastero'},
        {'codigo': 'TRINITARIO', 'nombre': 'Trinitario', 'descripcion': 'Variedad de cacao trinitario'},
    ]
    for var in variedades:
        VariedadCacao.objects.get_or_create(codigo=var['codigo'], defaults=var)
    
    # Create TipoSuelo
    tipos_suelo = [
        {'codigo': 'ARCILLOSO', 'nombre': 'Arcilloso', 'descripcion': 'Suelo arcilloso'},
        {'codigo': 'ARENOSO', 'nombre': 'Arenoso', 'descripcion': 'Suelo arenoso'},
        {'codigo': 'LIMOSO', 'nombre': 'Limoso', 'descripcion': 'Suelo limoso'},
        {'codigo': 'FRANCO', 'nombre': 'Franco', 'descripcion': 'Suelo franco'},
    ]
    for ts in tipos_suelo:
        TipoSuelo.objects.get_or_create(codigo=ts['codigo'], defaults=ts)
    
    # Create Clima
    climas = [
        {'codigo': 'TROPICAL', 'nombre': 'Tropical', 'descripcion': 'Clima tropical'},
        {'codigo': 'SUBTROPICAL', 'nombre': 'Subtropical', 'descripcion': 'Clima subtropical'},
        {'codigo': 'TEMPLADO', 'nombre': 'Templado', 'descripcion': 'Clima templado'},
    ]
    for cl in climas:
        Clima.objects.get_or_create(codigo=cl['codigo'], defaults=cl)
    
    # Create EstadoFinca
    estados_finca = [
        {'codigo': 'ACTIVA', 'nombre': 'Activa', 'descripcion': 'Finca activa'},
        {'codigo': 'INACTIVA', 'nombre': 'Inactiva', 'descripcion': 'Finca inactiva'},
        {'codigo': 'SUSPENDIDA', 'nombre': 'Suspendida', 'descripcion': 'Finca suspendida'},
    ]
    for ef in estados_finca:
        EstadoFinca.objects.get_or_create(codigo=ef['codigo'], defaults=ef)
    
    # Create EstadoLote
    estados_lote = [
        {'codigo': 'ACTIVO', 'nombre': 'Activo', 'descripcion': 'Lote activo'},
        {'codigo': 'INACTIVO', 'nombre': 'Inactivo', 'descripcion': 'Lote inactivo'},
        {'codigo': 'COSECHADO', 'nombre': 'Cosechado', 'descripcion': 'Lote cosechado'},
        {'codigo': 'RENOVADO', 'nombre': 'Renovado', 'descripcion': 'Lote renovado'},
    ]
    for el in estados_lote:
        EstadoLote.objects.get_or_create(codigo=el['codigo'], defaults=el)


def reverse_create_initial_catalog_data(apps, schema_editor):
    """Reverse migration - delete catalog data."""
    VariedadCacao = apps.get_model('catalogos', 'VariedadCacao')
    TipoSuelo = apps.get_model('catalogos', 'TipoSuelo')
    Clima = apps.get_model('catalogos', 'Clima')
    EstadoFinca = apps.get_model('catalogos', 'EstadoFinca')
    EstadoLote = apps.get_model('catalogos', 'EstadoLote')
    
    VariedadCacao.objects.all().delete()
    TipoSuelo.objects.all().delete()
    Clima.objects.all().delete()
    EstadoFinca.objects.all().delete()
    EstadoLote.objects.all().delete()


def remove_duplicate_indexes(apps, schema_editor):
    """Remove duplicate indexes if they exist."""
    db_alias = schema_editor.connection.alias
    with connection.cursor() as cursor:
        # Remove duplicate indexes if they exist
        indexes_to_remove = [
            'catalogos_e_codigo_idx',
            'catalogos_e_activo_idx',
        ]
        for index_name in indexes_to_remove:
            try:
                cursor.execute("""
                    SELECT 1 FROM pg_indexes 
                    WHERE indexname = %s
                """, [index_name])
                if cursor.fetchone():
                    cursor.execute(f'DROP INDEX IF EXISTS {index_name} CASCADE')
                    print(f"Removed duplicate index: {index_name}")
            except Exception as e:
                print(f"Error removing index {index_name}: {e}")


def reverse_remove_duplicate_indexes(apps, schema_editor):
    """Reverse - do nothing."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('catalogos', '0003_add_string_defaults'),
    ]

    operations = [
        migrations.CreateModel(
            name='VariedadCacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(help_text='Código único de la variedad (ej: CRIOLLO, FORASTERO)', max_length=20, unique=True)),
                ('nombre', models.CharField(help_text='Nombre de la variedad (ej: Criollo, Forastero, Trinitario)', max_length=100)),
                ('descripcion', models.TextField(blank=True, default='', help_text='Descripción de la variedad')),
                ('activo', models.BooleanField(default=True, help_text='Indica si la variedad está activa')),
            ],
            options={
                'verbose_name': 'Variedad de Cacao',
                'verbose_name_plural': 'Variedades de Cacao',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='TipoSuelo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(help_text='Código único del tipo de suelo', max_length=20, unique=True)),
                ('nombre', models.CharField(help_text='Nombre del tipo de suelo', max_length=100)),
                ('descripcion', models.TextField(blank=True, default='', help_text='Descripción del tipo de suelo')),
                ('activo', models.BooleanField(default=True, help_text='Indica si el tipo está activo')),
            ],
            options={
                'verbose_name': 'Tipo de Suelo',
                'verbose_name_plural': 'Tipos de Suelo',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='Clima',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(help_text='Código único del tipo de clima', max_length=20, unique=True)),
                ('nombre', models.CharField(help_text='Nombre del tipo de clima', max_length=100)),
                ('descripcion', models.TextField(blank=True, default='', help_text='Descripción del tipo de clima')),
                ('activo', models.BooleanField(default=True, help_text='Indica si el tipo está activo')),
            ],
            options={
                'verbose_name': 'Clima',
                'verbose_name_plural': 'Climas',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='EstadoFinca',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(help_text='Código único del estado (ej: ACTIVA, INACTIVA)', max_length=20, unique=True)),
                ('nombre', models.CharField(help_text='Nombre del estado', max_length=100)),
                ('descripcion', models.TextField(blank=True, default='', help_text='Descripción del estado')),
                ('activo', models.BooleanField(default=True, help_text='Indica si el estado está activo')),
            ],
            options={
                'verbose_name': 'Estado de Finca',
                'verbose_name_plural': 'Estados de Finca',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='EstadoLote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(help_text='Código único del estado (ej: ACTIVO, INACTIVO)', max_length=20, unique=True)),
                ('nombre', models.CharField(help_text='Nombre del estado', max_length=100)),
                ('descripcion', models.TextField(blank=True, default='', help_text='Descripción del estado')),
                ('activo', models.BooleanField(default=True, help_text='Indica si el estado está activo')),
            ],
            options={
                'verbose_name': 'Estado de Lote',
                'verbose_name_plural': 'Estados de Lote',
                'ordering': ['nombre'],
            },
        ),
        # Remove duplicate indexes BEFORE creating new ones
        migrations.RunPython(
            remove_duplicate_indexes,
            reverse_remove_duplicate_indexes,
        ),
        migrations.AddIndex(
            model_name='variedadcacao',
            index=models.Index(fields=['codigo'], name='catalogos_variedadcacao_codigo_idx'),
        ),
        migrations.AddIndex(
            model_name='variedadcacao',
            index=models.Index(fields=['activo'], name='catalogos_variedadcacao_activo_idx'),
        ),
        migrations.AddIndex(
            model_name='tiposuelo',
            index=models.Index(fields=['codigo'], name='catalogos_tiposuelo_codigo_idx'),
        ),
        migrations.AddIndex(
            model_name='tiposuelo',
            index=models.Index(fields=['activo'], name='catalogos_tiposuelo_activo_idx'),
        ),
        migrations.AddIndex(
            model_name='clima',
            index=models.Index(fields=['codigo'], name='catalogos_clima_codigo_idx'),
        ),
        migrations.AddIndex(
            model_name='clima',
            index=models.Index(fields=['activo'], name='catalogos_clima_activo_idx'),
        ),
        migrations.AddIndex(
            model_name='estadofinca',
            index=models.Index(fields=['codigo'], name='catalogos_estadofinca_codigo_idx'),
        ),
        migrations.AddIndex(
            model_name='estadofinca',
            index=models.Index(fields=['activo'], name='catalogos_estadofinca_activo_idx'),
        ),
        migrations.AddIndex(
            model_name='estadolote',
            index=models.Index(fields=['codigo'], name='catalogos_estadolote_codigo_idx'),
        ),
        migrations.AddIndex(
            model_name='estadolote',
            index=models.Index(fields=['activo'], name='catalogos_estadolote_activo_idx'),
        ),
        # Create initial catalog data
        migrations.RunPython(
            create_initial_catalog_data,
            reverse_create_initial_catalog_data,
        ),
    ]

