# Generated manually - Migrate Lote catalog FKs to Parametro
# Phase 2 of catalog unification: Update Foreign Keys in Lote
# -*- coding: utf-8 -*-

from django.db import migrations, models
import django.db.models.deletion


def migrate_lote_catalogs_to_parametros(apps, schema_editor):
    """
    Migrate Lote catalog ForeignKeys to Parametro.
    Updates: variedad, estado
    """
    Lote = apps.get_model('fincas_app', 'Lote')
    Parametro = apps.get_model('catalogos', 'Parametro')
    Tema = apps.get_model('catalogos', 'Tema')
    
    # Get themes
    tema_variedad = Tema.objects.get(codigo='TEMA_VARIEDAD_CACAO')
    tema_estado_lote = Tema.objects.get(codigo='TEMA_ESTADO_LOTE')
    
    # Create mapping function
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
    
    # Migrate variedad
    lotes = Lote.objects.exclude(variedad__isnull=True)
    migrated_variedad = 0
    for lote in lotes:
        parametro = get_parametro_by_catalog_id(tema_variedad, lote.variedad_id, 'VariedadCacao')
        if parametro:
            lote.variedad_parametro_id = parametro.id
            migrated_variedad += 1
    Lote.objects.bulk_update(lotes, ['variedad_parametro_id'])
    print(f"Migrated {migrated_variedad} variedad references")
    
    # Migrate estado
    lotes = Lote.objects.exclude(estado__isnull=True)
    migrated_estado = 0
    for lote in lotes:
        parametro = get_parametro_by_catalog_id(tema_estado_lote, lote.estado_id, 'EstadoLote')
        if parametro:
            lote.estado_parametro_id = parametro.id
            migrated_estado += 1
    Lote.objects.bulk_update(lotes, ['estado_parametro_id'])
    print(f"Migrated {migrated_estado} estado references")


def reverse_migrate_lote_catalogs(apps, schema_editor):
    """Reverse migration - not fully supported."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('fincas_app', '0020_migrate_finca_catalogs_to_parametros'),
        ('catalogos', '0013_create_themes_and_migrate_catalogs'),
    ]

    operations = [
        # Add temporary columns
        migrations.AddField(
            model_name='lote',
            name='variedad_parametro',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=models.PROTECT,
                related_name='lotes_variedad_temp',
                to='catalogos.parametro',
                help_text='Variedad (temporal - migración)'
            ),
        ),
        migrations.AddField(
            model_name='lote',
            name='estado_parametro',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=models.PROTECT,
                related_name='lotes_estado_temp',
                to='catalogos.parametro',
                help_text='Estado (temporal - migración)'
            ),
        ),
        # Migrate data
        migrations.RunPython(
            migrate_lote_catalogs_to_parametros,
            reverse_migrate_lote_catalogs,
        ),
        # Remove old FKs
        migrations.RemoveField(
            model_name='lote',
            name='variedad',
        ),
        migrations.RemoveField(
            model_name='lote',
            name='estado',
        ),
        # Rename temporary columns
        migrations.RenameField(
            model_name='lote',
            old_name='variedad_parametro',
            new_name='variedad',
        ),
        migrations.RenameField(
            model_name='lote',
            old_name='estado_parametro',
            new_name='estado',
        ),
        # Update FK definitions
        migrations.AlterField(
            model_name='lote',
            name='variedad',
            field=models.ForeignKey(
                on_delete=models.PROTECT,
                related_name='lotes',
                to='catalogos.parametro',
                help_text='Variedad de cacao del lote'
            ),
        ),
        migrations.AlterField(
            model_name='lote',
            name='estado',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=models.PROTECT,
                related_name='lotes',
                to='catalogos.parametro',
                help_text='Estado actual del lote'
            ),
        ),
    ]

