# Generated manually - Migrate ReporteGenerado catalog FKs to Parametro
# Phase 2 of catalog unification: Update Foreign Keys in reports
# -*- coding: utf-8 -*-

from django.db import migrations, models
import django.db.models.deletion


def migrate_report_catalogs_to_parametros(apps, schema_editor):
    """
    Migrate ReporteGenerado catalog ForeignKeys to Parametro.
    Updates: tipo_reporte, formato, estado
    """
    ReporteGenerado = apps.get_model('reports', 'ReporteGenerado')
    Parametro = apps.get_model('catalogos', 'Parametro')
    Tema = apps.get_model('catalogos', 'Tema')
    
    # Get themes
    tema_tipo_reporte = Tema.objects.get(codigo='TEMA_TIPO_REPORTE')
    tema_formato_reporte = Tema.objects.get(codigo='TEMA_FORMATO_REPORTE')
    tema_estado_reporte = Tema.objects.get(codigo='TEMA_ESTADO_REPORTE')
    
    # Mapping function
    def get_parametro_by_catalog_id(tema, old_catalog_id, catalog_model_name):
        """Get parametro by old catalog ID."""
        if not old_catalog_id:
            return None
        
        try:
            CatalogModel = apps.get_model('catalogos', catalog_model_name)
            old_record = CatalogModel.objects.get(id=old_catalog_id)
            parametro = Parametro.objects.get(tema=tema, codigo=old_record.codigo)
            return parametro
        except (CatalogModel.DoesNotExist, Parametro.DoesNotExist):
            print(f"Warning: Could not find parametro for {catalog_model_name} id={old_catalog_id}")
            return None
    
    # Migrate tipo_reporte
    reportes = ReporteGenerado.objects.exclude(tipo_reporte__isnull=True)
    migrated_tipo_reporte = 0
    for reporte in reportes:
        parametro = get_parametro_by_catalog_id(tema_tipo_reporte, reporte.tipo_reporte_id, 'TipoReporte')
        if parametro:
            reporte.tipo_reporte_parametro_id = parametro.id
            migrated_tipo_reporte += 1
    ReporteGenerado.objects.bulk_update(reportes, ['tipo_reporte_parametro_id'])
    print(f"Migrated {migrated_tipo_reporte} tipo_reporte references")
    
    # Migrate formato
    reportes = ReporteGenerado.objects.exclude(formato__isnull=True)
    migrated_formato = 0
    for reporte in reportes:
        parametro = get_parametro_by_catalog_id(tema_formato_reporte, reporte.formato_id, 'FormatoReporte')
        if parametro:
            reporte.formato_parametro_id = parametro.id
            migrated_formato += 1
    ReporteGenerado.objects.bulk_update(reportes, ['formato_parametro_id'])
    print(f"Migrated {migrated_formato} formato references")
    
    # Migrate estado
    reportes = ReporteGenerado.objects.exclude(estado__isnull=True)
    migrated_estado = 0
    for reporte in reportes:
        parametro = get_parametro_by_catalog_id(tema_estado_reporte, reporte.estado_id, 'EstadoReporte')
        if parametro:
            reporte.estado_parametro_id = parametro.id
            migrated_estado += 1
    ReporteGenerado.objects.bulk_update(reportes, ['estado_parametro_id'])
    print(f"Migrated {migrated_estado} estado references")


def reverse_migrate_report_catalogs(apps, schema_editor):
    """Reverse migration - not fully supported."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0008_remove_reportegenerado_api_reportegenerado_tipo_reporte_idx_and_more'),
        ('catalogos', '0013_create_themes_and_migrate_catalogs'),
    ]

    operations = [
        # Add temporary columns
        migrations.AddField(
            model_name='reportegenerado',
            name='tipo_reporte_parametro',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=models.PROTECT,
                related_name='reportes_tipo_reporte_temp',
                to='catalogos.parametro',
                help_text='Tipo de reporte (temporal - migración)'
            ),
        ),
        migrations.AddField(
            model_name='reportegenerado',
            name='formato_parametro',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=models.PROTECT,
                related_name='reportes_formato_temp',
                to='catalogos.parametro',
                help_text='Formato (temporal - migración)'
            ),
        ),
        migrations.AddField(
            model_name='reportegenerado',
            name='estado_parametro',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=models.PROTECT,
                related_name='reportes_estado_temp',
                to='catalogos.parametro',
                help_text='Estado (temporal - migración)'
            ),
        ),
        # Migrate data
        migrations.RunPython(
            migrate_report_catalogs_to_parametros,
            reverse_migrate_report_catalogs,
        ),
        # Remove old FKs
        migrations.RemoveField(
            model_name='reportegenerado',
            name='tipo_reporte',
        ),
        migrations.RemoveField(
            model_name='reportegenerado',
            name='formato',
        ),
        migrations.RemoveField(
            model_name='reportegenerado',
            name='estado',
        ),
        # Rename temporary columns
        migrations.RenameField(
            model_name='reportegenerado',
            old_name='tipo_reporte_parametro',
            new_name='tipo_reporte',
        ),
        migrations.RenameField(
            model_name='reportegenerado',
            old_name='formato_parametro',
            new_name='formato',
        ),
        migrations.RenameField(
            model_name='reportegenerado',
            old_name='estado_parametro',
            new_name='estado',
        ),
        # Update FK definitions
        migrations.AlterField(
            model_name='reportegenerado',
            name='tipo_reporte',
            field=models.ForeignKey(
                on_delete=models.PROTECT,
                related_name='reportes',
                to='catalogos.parametro',
                help_text='Tipo de reporte'
            ),
        ),
        migrations.AlterField(
            model_name='reportegenerado',
            name='formato',
            field=models.ForeignKey(
                on_delete=models.PROTECT,
                related_name='reportes',
                to='catalogos.parametro',
                help_text='Formato del reporte'
            ),
        ),
        migrations.AlterField(
            model_name='reportegenerado',
            name='estado',
            field=models.ForeignKey(
                on_delete=models.PROTECT,
                related_name='reportes',
                to='catalogos.parametro',
                help_text='Estado del reporte'
            ),
        ),
    ]

