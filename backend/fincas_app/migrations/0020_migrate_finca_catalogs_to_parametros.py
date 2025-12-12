# Generated manually - Migrate Finca catalog FKs to Parametro
# Phase 2 of catalog unification: Update Foreign Keys in fincas_app
# -*- coding: utf-8 -*-

from django.db import migrations, models
import django.db.models.deletion


def migrate_finca_catalogs_to_parametros(apps, schema_editor):
    """
    Migrate Finca catalog ForeignKeys to Parametro.
    Updates: tipo_suelo, clima, estado
    """
    Finca = apps.get_model('fincas_app', 'Finca')
    Parametro = apps.get_model('catalogos', 'Parametro')
    Tema = apps.get_model('catalogos', 'Tema')
    
    # Get themes
    tema_tipo_suelo = Tema.objects.get(codigo='TEMA_TIPO_SUELO')
    tema_clima = Tema.objects.get(codigo='TEMA_CLIMA')
    tema_estado_finca = Tema.objects.get(codigo='TEMA_ESTADO_FINCA')
    
    # Create mapping functions
    def get_parametro_by_catalog_id(tema, old_catalog_id, catalog_model_name):
        """Get parametro by old catalog ID."""
        if not old_catalog_id:
            return None
        
        try:
            # Get old catalog record
            CatalogModel = apps.get_model('catalogos', catalog_model_name)
            old_record = CatalogModel.objects.get(id=old_catalog_id)
            
            # Find parametro by tema and codigo
            parametro = Parametro.objects.get(tema=tema, codigo=old_record.codigo)
            return parametro
        except (CatalogModel.DoesNotExist, Parametro.DoesNotExist):
            print(f"Warning: Could not find parametro for {catalog_model_name} id={old_catalog_id}")
            return None
    
    # Migrate tipo_suelo
    fincas = Finca.objects.exclude(tipo_suelo__isnull=True)
    migrated_tipo_suelo = 0
    for finca in fincas:
        parametro = get_parametro_by_catalog_id(tema_tipo_suelo, finca.tipo_suelo_id, 'TipoSuelo')
        if parametro:
            finca.tipo_suelo_parametro_id = parametro.id
            migrated_tipo_suelo += 1
    Finca.objects.bulk_update(fincas, ['tipo_suelo_parametro_id'])
    print(f"Migrated {migrated_tipo_suelo} tipo_suelo references")
    
    # Migrate clima
    fincas = Finca.objects.exclude(clima__isnull=True)
    migrated_clima = 0
    for finca in fincas:
        parametro = get_parametro_by_catalog_id(tema_clima, finca.clima_id, 'Clima')
        if parametro:
            finca.clima_parametro_id = parametro.id
            migrated_clima += 1
    Finca.objects.bulk_update(fincas, ['clima_parametro_id'])
    print(f"Migrated {migrated_clima} clima references")
    
    # Migrate estado
    fincas = Finca.objects.exclude(estado__isnull=True)
    migrated_estado = 0
    for finca in fincas:
        parametro = get_parametro_by_catalog_id(tema_estado_finca, finca.estado_id, 'EstadoFinca')
        if parametro:
            finca.estado_parametro_id = parametro.id
            migrated_estado += 1
    Finca.objects.bulk_update(fincas, ['estado_parametro_id'])
    print(f"Migrated {migrated_estado} estado references")


def reverse_migrate_finca_catalogs(apps, schema_editor):
    """
    Reverse migration: This is complex and may not be fully reversible.
    We would need to map back from parametro to old catalog.
    """
    # This is a one-way migration - reverse is not fully supported
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('fincas_app', '0019_final_2nf_verification'),
        ('catalogos', '0013_create_themes_and_migrate_catalogs'),
    ]

    operations = [
        # Add temporary columns
        migrations.AddField(
            model_name='finca',
            name='tipo_suelo_parametro',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=models.PROTECT,
                related_name='fincas_tipo_suelo_temp',
                to='catalogos.parametro',
                help_text='Tipo de suelo (temporal - migración)'
            ),
        ),
        migrations.AddField(
            model_name='finca',
            name='clima_parametro',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=models.PROTECT,
                related_name='fincas_clima_temp',
                to='catalogos.parametro',
                help_text='Clima (temporal - migración)'
            ),
        ),
        migrations.AddField(
            model_name='finca',
            name='estado_parametro',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=models.PROTECT,
                related_name='fincas_estado_temp',
                to='catalogos.parametro',
                help_text='Estado (temporal - migración)'
            ),
        ),
        # Migrate data
        migrations.RunPython(
            migrate_finca_catalogs_to_parametros,
            reverse_migrate_finca_catalogs,
        ),
        # Remove old FKs
        migrations.RemoveField(
            model_name='finca',
            name='tipo_suelo',
        ),
        migrations.RemoveField(
            model_name='finca',
            name='clima',
        ),
        migrations.RemoveField(
            model_name='finca',
            name='estado',
        ),
        # Rename temporary columns
        migrations.RenameField(
            model_name='finca',
            old_name='tipo_suelo_parametro',
            new_name='tipo_suelo',
        ),
        migrations.RenameField(
            model_name='finca',
            old_name='clima_parametro',
            new_name='clima',
        ),
        migrations.RenameField(
            model_name='finca',
            old_name='estado_parametro',
            new_name='estado',
        ),
        # Update FK definitions
        migrations.AlterField(
            model_name='finca',
            name='tipo_suelo',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=models.PROTECT,
                related_name='fincas',
                to='catalogos.parametro',
                help_text='Tipo de suelo de la finca'
            ),
        ),
        migrations.AlterField(
            model_name='finca',
            name='clima',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=models.PROTECT,
                related_name='fincas',
                to='catalogos.parametro',
                help_text='Tipo de clima de la finca'
            ),
        ),
        migrations.AlterField(
            model_name='finca',
            name='estado',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=models.PROTECT,
                related_name='fincas',
                to='catalogos.parametro',
                help_text='Estado de la finca'
            ),
        ),
    ]

