# Generated migration to normalize device_used and model_version fields (3NF normalization)
# -*- coding: utf-8 -*-
from django.db import migrations, models
import django.db.models.deletion


def normalize_prediction_ml_data(apps, schema_editor):
    """
    Migrate device_used and model_version from CharField to ForeignKeys.
    Maps existing values to Parametro catalog entries.
    """
    CacaoPrediction = apps.get_model('images_app', 'CacaoPrediction')
    Parametro = apps.get_model('catalogos', 'Parametro')
    Tema = apps.get_model('catalogos', 'Tema')
    
    # Get themes
    try:
        tema_tipo_dispositivo = Tema.objects.get(codigo='TEMA_TIPO_DISPOSITIVO')
        tema_version_modelo = Tema.objects.get(codigo='TEMA_VERSION_MODELO')
    except Tema.DoesNotExist:
        print("WARNING: Required themes not found. Skipping prediction ML fields migration.")
        return
    
    # Map of device codes
    device_map = {
        'cpu': 'CPU',
        'cuda': 'CUDA',
        'mps': 'MPS',
    }
    
    # Migrate device_used
    predictions = CacaoPrediction.objects.exclude(device_used='').exclude(device_used__isnull=True)
    migrated_device = 0
    
    for prediction in predictions:
        device_str = prediction.device_used.strip().lower()
        codigo = device_map.get(device_str, device_str.upper())
        
        try:
            parametro = Parametro.objects.get(tema=tema_tipo_dispositivo, codigo=codigo)
            prediction.device_used_fk = parametro
            migrated_device += 1
        except Parametro.DoesNotExist:
            # Default to CPU if not found
            try:
                parametro_default = Parametro.objects.get(tema=tema_tipo_dispositivo, codigo='CPU')
                prediction.device_used_fk = parametro_default
                migrated_device += 1
            except Parametro.DoesNotExist:
                print(f"Warning: Could not migrate device_used '{prediction.device_used}' for prediction {prediction.id}")
    
    # Migrate model_version
    predictions = CacaoPrediction.objects.exclude(model_version='').exclude(model_version__isnull=True)
    migrated_version = 0
    
    for prediction in predictions:
        version_str = prediction.model_version.strip()
        
        # Try to find by exact code match
        try:
            parametro = Parametro.objects.get(tema=tema_version_modelo, codigo=version_str)
            prediction.model_version_fk = parametro
            migrated_version += 1
        except Parametro.DoesNotExist:
            # Try to create if it doesn't exist (for dynamic versions)
            try:
                parametro = Parametro.objects.create(
                    tema=tema_version_modelo,
                    codigo=version_str,
                    nombre=version_str,
                    descripcion=f'Versión {version_str} del modelo',
                    activo=True
                )
                prediction.model_version_fk = parametro
                migrated_version += 1
            except Exception as e:
                # Default to v1.0 if creation fails
                try:
                    parametro_default = Parametro.objects.get(tema=tema_version_modelo, codigo='v1.0')
                    prediction.model_version_fk = parametro_default
                    migrated_version += 1
                except Parametro.DoesNotExist:
                    print(f"Warning: Could not migrate model_version '{prediction.model_version}' for prediction {prediction.id}")
    
    # Save all predictions
    CacaoPrediction.objects.bulk_update(
        [p for p in predictions if hasattr(p, 'device_used_fk') or hasattr(p, 'model_version_fk')],
        ['device_used_fk', 'model_version_fk'],
        batch_size=100
    )
    
    print(f"Migrated {migrated_device} device_used, {migrated_version} model_version")


def reverse_normalize_prediction_ml_data(apps, schema_editor):
    """
    Reverse migration - populate device_used and model_version from ForeignKeys.
    """
    CacaoPrediction = apps.get_model('images_app', 'CacaoPrediction')
    
    predictions = CacaoPrediction.objects.exclude(device_used_fk__isnull=True)
    for prediction in predictions:
        if prediction.device_used_fk:
            prediction.device_used = prediction.device_used_fk.codigo.lower()
            prediction.save(update_fields=['device_used'])
    
    predictions = CacaoPrediction.objects.exclude(model_version_fk__isnull=True)
    for prediction in predictions:
        if prediction.model_version_fk:
            prediction.model_version = prediction.model_version_fk.codigo
            prediction.save(update_fields=['model_version'])


class Migration(migrations.Migration):

    dependencies = [
        ('catalogos', '0013_create_themes_and_migrate_catalogs'),  # Use unified catalog system
        ('images_app', '0011_normalize_file_type'),
    ]

    operations = [
        # Add new ForeignKey fields (nullable initially)
        migrations.AddField(
            model_name='cacaoprediction',
            name='device_used_fk',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='predictions',
                to='catalogos.parametro',
                limit_choices_to={'tema__codigo': 'TEMA_TIPO_DISPOSITIVO'},
                help_text='Dispositivo usado para procesamiento (normalizado)'
            ),
        ),
        migrations.AddField(
            model_name='cacaoprediction',
            name='model_version_fk',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='predictions',
                to='catalogos.parametro',
                limit_choices_to={'tema__codigo': 'TEMA_VERSION_MODELO'},
                help_text='Versión del modelo usado (normalizado)'
            ),
        ),
        # Migrate data from CharField to ForeignKeys
        migrations.RunPython(
            normalize_prediction_ml_data,
            reverse_normalize_prediction_ml_data,
        ),
        # Remove old CharField columns
        migrations.RemoveField(
            model_name='cacaoprediction',
            name='device_used',
        ),
        migrations.RemoveField(
            model_name='cacaoprediction',
            name='model_version',
        ),
        # Rename ForeignKey fields to final names
        migrations.RenameField(
            model_name='cacaoprediction',
            old_name='device_used_fk',
            new_name='device_used',
        ),
        migrations.RenameField(
            model_name='cacaoprediction',
            old_name='model_version_fk',
            new_name='model_version',
        ),
        # Make fields NOT NULL (after data migration)
        # Note: Django automatically creates indexes for ForeignKeys, so we don't need explicit AddIndex
        migrations.AlterField(
            model_name='cacaoprediction',
            name='device_used',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='predictions',
                to='catalogos.parametro',
                limit_choices_to={'tema__codigo': 'TEMA_TIPO_DISPOSITIVO'},
                help_text='Dispositivo usado para procesamiento (normalizado)'
            ),
        ),
        migrations.AlterField(
            model_name='cacaoprediction',
            name='model_version',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='predictions',
                to='catalogos.parametro',
                limit_choices_to={'tema__codigo': 'TEMA_VERSION_MODELO'},
                help_text='Versión del modelo usado (normalizado)'
            ),
        ),
    ]

