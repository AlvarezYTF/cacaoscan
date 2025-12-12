# Generated manually - Migrate CacaoImage and CacaoPrediction catalog FKs to Parametro
# Phase 2 of catalog unification: Update Foreign Keys in images_app
# -*- coding: utf-8 -*-

from django.db import migrations, models
import django.db.models.deletion


def migrate_image_catalogs_to_parametros(apps, schema_editor):
    """
    Migrate CacaoImage and CacaoPrediction catalog ForeignKeys to Parametro.
    Updates: CacaoImage.file_type, CacaoPrediction.model_version, CacaoPrediction.device_used
    """
    CacaoImage = apps.get_model('images_app', 'CacaoImage')
    CacaoPrediction = apps.get_model('images_app', 'CacaoPrediction')
    Parametro = apps.get_model('catalogos', 'Parametro')
    Tema = apps.get_model('catalogos', 'Tema')
    
    # Get themes
    tema_tipo_archivo = Tema.objects.get(codigo='TEMA_TIPO_ARCHIVO')
    tema_version_modelo = Tema.objects.get(codigo='TEMA_VERSION_MODELO')
    tema_tipo_dispositivo = Tema.objects.get(codigo='TEMA_TIPO_DISPOSITIVO')
    
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
    
    # Migrate CacaoImage.file_type
    images = CacaoImage.objects.exclude(file_type__isnull=True)
    migrated_file_type = 0
    for image in images:
        parametro = get_parametro_by_catalog_id(tema_tipo_archivo, image.file_type_id, 'TipoArchivo')
        if parametro:
            image.file_type_parametro_id = parametro.id
            migrated_file_type += 1
    CacaoImage.objects.bulk_update(images, ['file_type_parametro_id'])
    print(f"Migrated {migrated_file_type} file_type references")
    
    # Migrate CacaoPrediction.model_version
    predictions = CacaoPrediction.objects.exclude(model_version__isnull=True)
    migrated_model_version = 0
    for prediction in predictions:
        parametro = get_parametro_by_catalog_id(tema_version_modelo, prediction.model_version_id, 'VersionModelo')
        if parametro:
            prediction.model_version_parametro_id = parametro.id
            migrated_model_version += 1
    CacaoPrediction.objects.bulk_update(predictions, ['model_version_parametro_id'])
    print(f"Migrated {migrated_model_version} model_version references")
    
    # Migrate CacaoPrediction.device_used
    predictions = CacaoPrediction.objects.exclude(device_used__isnull=True)
    migrated_device_used = 0
    for prediction in predictions:
        parametro = get_parametro_by_catalog_id(tema_tipo_dispositivo, prediction.device_used_id, 'TipoDispositivo')
        if parametro:
            prediction.device_used_parametro_id = parametro.id
            migrated_device_used += 1
    CacaoPrediction.objects.bulk_update(predictions, ['device_used_parametro_id'])
    print(f"Migrated {migrated_device_used} device_used references")


def reverse_migrate_image_catalogs(apps, schema_editor):
    """Reverse migration - not fully supported."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('images_app', '0012_normalize_prediction_ml_fields'),
        ('catalogos', '0013_create_themes_and_migrate_catalogs'),
    ]

    operations = [
        # Add temporary columns for CacaoImage
        migrations.AddField(
            model_name='cacaoimage',
            name='file_type_parametro',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=models.PROTECT,
                related_name='cacao_images_file_type_temp',
                to='catalogos.parametro',
                help_text='Tipo de archivo (temporal - migración)'
            ),
        ),
        # Add temporary columns for CacaoPrediction
        migrations.AddField(
            model_name='cacaoprediction',
            name='model_version_parametro',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=models.PROTECT,
                related_name='predictions_model_version_temp',
                to='catalogos.parametro',
                help_text='Versión del modelo (temporal - migración)'
            ),
        ),
        migrations.AddField(
            model_name='cacaoprediction',
            name='device_used_parametro',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=models.PROTECT,
                related_name='predictions_device_used_temp',
                to='catalogos.parametro',
                help_text='Dispositivo usado (temporal - migración)'
            ),
        ),
        # Migrate data
        migrations.RunPython(
            migrate_image_catalogs_to_parametros,
            reverse_migrate_image_catalogs,
        ),
        # Remove old FKs
        migrations.RemoveField(
            model_name='cacaoimage',
            name='file_type',
        ),
        migrations.RemoveField(
            model_name='cacaoprediction',
            name='model_version',
        ),
        migrations.RemoveField(
            model_name='cacaoprediction',
            name='device_used',
        ),
        # Rename temporary columns
        migrations.RenameField(
            model_name='cacaoimage',
            old_name='file_type_parametro',
            new_name='file_type',
        ),
        migrations.RenameField(
            model_name='cacaoprediction',
            old_name='model_version_parametro',
            new_name='model_version',
        ),
        migrations.RenameField(
            model_name='cacaoprediction',
            old_name='device_used_parametro',
            new_name='device_used',
        ),
        # Update FK definitions
        migrations.AlterField(
            model_name='cacaoimage',
            name='file_type',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=models.PROTECT,
                related_name='cacao_images',
                to='catalogos.parametro',
                help_text='Tipo de archivo (normalizado)'
            ),
        ),
        migrations.AlterField(
            model_name='cacaoprediction',
            name='model_version',
            field=models.ForeignKey(
                on_delete=models.PROTECT,
                related_name='predictions',
                to='catalogos.parametro',
                help_text='Versión del modelo usado (normalizado)'
            ),
        ),
        migrations.AlterField(
            model_name='cacaoprediction',
            name='device_used',
            field=models.ForeignKey(
                on_delete=models.PROTECT,
                related_name='predictions',
                to='catalogos.parametro',
                help_text='Dispositivo usado para procesamiento (normalizado)'
            ),
        ),
    ]

