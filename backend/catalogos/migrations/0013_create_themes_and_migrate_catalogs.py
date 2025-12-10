# Generated manually - Create themes and migrate catalog data to parameters
# This is Phase 1 of the catalog unification migration
# -*- coding: utf-8 -*-

from django.db import migrations, models


def create_themes_and_migrate_catalogs(apps, schema_editor):
    """
    Create themes for each catalog and migrate all catalog records to parameters.
    This preserves all existing data while moving it to the unified catalog system.
    """
    Tema = apps.get_model('catalogos', 'Tema')
    Parametro = apps.get_model('catalogos', 'Parametro')
    
    # Mapping: (catalog_model_name, tema_codigo, tema_nombre)
    catalog_mappings = [
        ('Clima', 'TEMA_CLIMA', 'Tipo de Clima'),
        ('EstadoFinca', 'TEMA_ESTADO_FINCA', 'Estado de Finca'),
        ('EstadoLote', 'TEMA_ESTADO_LOTE', 'Estado de Lote'),
        ('EstadoReporte', 'TEMA_ESTADO_REPORTE', 'Estado de Reporte'),
        ('FormatoReporte', 'TEMA_FORMATO_REPORTE', 'Formato de Reporte'),
        ('TipoArchivo', 'TEMA_TIPO_ARCHIVO', 'Tipo de Archivo'),
        ('TipoDispositivo', 'TEMA_TIPO_DISPOSITIVO', 'Tipo de Dispositivo'),
        ('TipoNotificacion', 'TEMA_TIPO_NOTIFICACION', 'Tipo de Notificación'),
        ('TipoReporte', 'TEMA_TIPO_REPORTE', 'Tipo de Reporte'),
        ('TipoSuelo', 'TEMA_TIPO_SUELO', 'Tipo de Suelo'),
        ('VariedadCacao', 'TEMA_VARIEDAD_CACAO', 'Variedad de Cacao'),
        ('VersionModelo', 'TEMA_VERSION_MODELO', 'Versión de Modelo'),
    ]
    
    # Create themes and migrate data
    for catalog_model_name, tema_codigo, tema_nombre in catalog_mappings:
        try:
            CatalogModel = apps.get_model('catalogos', catalog_model_name)
        except LookupError:
            print(f"Warning: Catalog model {catalog_model_name} not found, skipping...")
            continue
        
        # Create or get theme
        tema, created = Tema.objects.get_or_create(
            codigo=tema_codigo,
            defaults={
                'nombre': tema_nombre,
                'descripcion': f'Catálogo unificado para {tema_nombre}',
                'activo': True
            }
        )
        
        if created:
            print(f"Created theme: {tema_codigo}")
        else:
            print(f"Theme {tema_codigo} already exists, updating if needed...")
            tema.nombre = tema_nombre
            tema.descripcion = f'Catálogo unificado para {tema_nombre}'
            tema.activo = True
            tema.save()
        
        # Migrate catalog records to parameters
        catalog_records = CatalogModel.objects.all()
        migrated_count = 0
        
        for record in catalog_records:
            # Build description with additional fields if they exist
            descripcion = record.descripcion if hasattr(record, 'descripcion') else ''
            
            # Handle TipoArchivo: preserve mime_type in description
            if catalog_model_name == 'TipoArchivo' and hasattr(record, 'mime_type'):
                if descripcion:
                    descripcion += f" | MIME Type: {record.mime_type}"
                else:
                    descripcion = f"MIME Type: {record.mime_type}"
            
            # Handle VersionModelo: preserve fecha_lanzamiento in description
            if catalog_model_name == 'VersionModelo' and hasattr(record, 'fecha_lanzamiento'):
                fecha_str = record.fecha_lanzamiento.strftime('%Y-%m-%d') if record.fecha_lanzamiento else 'N/A'
                if descripcion:
                    descripcion += f" | Fecha Lanzamiento: {fecha_str}"
                else:
                    descripcion = f"Fecha Lanzamiento: {fecha_str}"
            
            # Create parameter
            parametro, created = Parametro.objects.get_or_create(
                tema=tema,
                codigo=record.codigo,
                defaults={
                    'nombre': record.nombre,
                    'descripcion': descripcion,
                    'activo': record.activo if hasattr(record, 'activo') else True
                }
            )
            
            if created:
                migrated_count += 1
            else:
                # Update if exists but different
                if parametro.nombre != record.nombre or parametro.descripcion != descripcion:
                    parametro.nombre = record.nombre
                    parametro.descripcion = descripcion
                    parametro.activo = record.activo if hasattr(record, 'activo') else True
                    parametro.save()
        
        print(f"Migrated {migrated_count} records from {catalog_model_name} to {tema_codigo}")


def reverse_create_themes_and_migrate_catalogs(apps, schema_editor):
    """
    Reverse migration: Delete themes and parameters created.
    Note: This does NOT restore the old catalog tables.
    """
    Tema = apps.get_model('catalogos', 'Tema')
    Parametro = apps.get_model('catalogos', 'Parametro')
    
    tema_codigos = [
        'TEMA_CLIMA', 'TEMA_ESTADO_FINCA', 'TEMA_ESTADO_LOTE',
        'TEMA_ESTADO_REPORTE', 'TEMA_FORMATO_REPORTE', 'TEMA_TIPO_ARCHIVO',
        'TEMA_TIPO_DISPOSITIVO', 'TEMA_TIPO_NOTIFICACION', 'TEMA_TIPO_REPORTE',
        'TEMA_TIPO_SUELO', 'TEMA_VARIEDAD_CACAO', 'TEMA_VERSION_MODELO'
    ]
    
    for tema_codigo in tema_codigos:
        try:
            tema = Tema.objects.get(codigo=tema_codigo)
            Parametro.objects.filter(tema=tema).delete()
            tema.delete()
            print(f"Deleted theme and parameters: {tema_codigo}")
        except Tema.DoesNotExist:
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('catalogos', '0012_rename_catalogos_t_codigo_archivo_idx_catalogos_t_codigo_aeb37b_idx_and_more'),
    ]

    operations = [
        # First, increase codigo field length to support longer tema codes (TEMA_TIPO_NOTIFICACION = 22 chars)
        migrations.AlterField(
            model_name='tema',
            name='codigo',
            field=models.CharField(help_text='Código único del tema (ej: TIPO_DOC, TEMA_TIPO_NOTIFICACION)', max_length=30, unique=True),
        ),
        migrations.RunPython(
            create_themes_and_migrate_catalogs,
            reverse_create_themes_and_migrate_catalogs,
        ),
    ]

