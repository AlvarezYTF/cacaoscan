# Generated migration to normalize file_type field (1NF normalization)
# -*- coding: utf-8 -*-
from django.db import migrations, models
import django.db.models.deletion


def normalize_file_type_data(apps, schema_editor):
    """
    Migrate file_type from CharField to ForeignKey to Parametro (TEMA_TIPO_ARCHIVO).
    Maps existing MIME types to Parametro catalog entries.
    """
    CacaoImage = apps.get_model('images_app', 'CacaoImage')
    Parametro = apps.get_model('catalogos', 'Parametro')
    Tema = apps.get_model('catalogos', 'Tema')
    
    # Get TEMA_TIPO_ARCHIVO theme
    try:
        tema_tipo_archivo = Tema.objects.get(codigo='TEMA_TIPO_ARCHIVO')
    except Tema.DoesNotExist:
        print("WARNING: TEMA_TIPO_ARCHIVO not found. Skipping file_type migration.")
        return
    
    # Map of MIME types to Parametro codigo
    mime_type_map = {
        'image/jpeg': 'IMAGE_JPEG',
        'image/jpg': 'IMAGE_JPG',
        'image/png': 'IMAGE_PNG',
        'image/webp': 'IMAGE_WEBP',
    }
    
    # Get all images with file_type
    images = CacaoImage.objects.exclude(file_type='').exclude(file_type__isnull=True)
    migrated = 0
    not_found = 0
    
    for image in images:
        file_type_str = image.file_type.strip().lower()
        
        # Try to find matching Parametro by MIME type
        parametro = None
        for mime_type, codigo in mime_type_map.items():
            if file_type_str == mime_type.lower():
                try:
                    parametro = Parametro.objects.get(tema=tema_tipo_archivo, codigo=codigo)
                    break
                except Parametro.DoesNotExist:
                    continue
        
        # If not found by exact match, try to find by partial match
        if not parametro:
            for mime_type, codigo in mime_type_map.items():
                if mime_type.lower() in file_type_str or file_type_str in mime_type.lower():
                    try:
                        parametro = Parametro.objects.get(tema=tema_tipo_archivo, codigo=codigo)
                        break
                    except Parametro.DoesNotExist:
                        continue
        
        # If still not found, try to find by searching in metadata.mime_type
        if not parametro:
            try:
                parametro = Parametro.objects.filter(
                    tema=tema_tipo_archivo,
                    metadata__mime_type__iexact=file_type_str
                ).first()
            except Exception:
                pass
        
        if parametro:
            image.file_type_fk = parametro
            image.save(update_fields=['file_type_fk'])
            migrated += 1
        else:
            # Default to JPEG if not found
            try:
                parametro_default = Parametro.objects.get(tema=tema_tipo_archivo, codigo='IMAGE_JPEG')
                image.file_type_fk = parametro_default
                image.save(update_fields=['file_type_fk'])
                migrated += 1
            except Parametro.DoesNotExist:
                not_found += 1
                print(f"Warning: Could not migrate file_type '{image.file_type}' for image {image.id}")
    
    print(f"Migrated {migrated} images, {not_found} not found")


def reverse_normalize_file_type_data(apps, schema_editor):
    """
    Reverse migration - populate file_type from file_type_fk.
    """
    CacaoImage = apps.get_model('images_app', 'CacaoImage')
    
    images = CacaoImage.objects.exclude(file_type_fk__isnull=True)
    for image in images:
        if image.file_type_fk:
            # Try to get mime_type from metadata, fallback to codigo
            mime_type = image.file_type_fk.metadata.get('mime_type', '') if image.file_type_fk.metadata else ''
            if not mime_type:
                mime_type = image.file_type_fk.codigo.lower().replace('_', '/')
            image.file_type = mime_type
            image.save(update_fields=['file_type'])


class Migration(migrations.Migration):

    dependencies = [
        ('catalogos', '0013_create_themes_and_migrate_catalogs'),  # Use unified catalog system
        ('images_app', '0010_migrate_api_cacaoimage_data'),
    ]

    operations = [
        # Add new ForeignKey field (nullable initially)
        migrations.AddField(
            model_name='cacaoimage',
            name='file_type_fk',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='cacao_images',
                to='catalogos.parametro',
                limit_choices_to={'tema__codigo': 'TEMA_TIPO_ARCHIVO'},
                help_text='Tipo de archivo (normalizado)'
            ),
        ),
        # Migrate data from file_type to file_type_fk
        migrations.RunPython(
            normalize_file_type_data,
            reverse_normalize_file_type_data,
        ),
        # Remove old CharField
        migrations.RemoveField(
            model_name='cacaoimage',
            name='file_type',
        ),
        # Rename file_type_fk to file_type
        migrations.RenameField(
            model_name='cacaoimage',
            old_name='file_type_fk',
            new_name='file_type',
        ),
        # Make file_type NOT NULL (after data migration)
        migrations.AlterField(
            model_name='cacaoimage',
            name='file_type',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='cacao_images',
                to='catalogos.parametro',
                limit_choices_to={'tema__codigo': 'TEMA_TIPO_ARCHIVO'},
                help_text='Tipo de archivo (normalizado)'
            ),
        ),
    ]

