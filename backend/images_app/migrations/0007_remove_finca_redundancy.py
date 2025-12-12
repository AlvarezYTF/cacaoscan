# Generated migration to remove finca redundancy from CacaoImage (2NF normalization)
# -*- coding: utf-8 -*-
from django.db import migrations


def verify_and_migrate_finca_data(apps, schema_editor):
    """
    Verify that all images with finca also have lote with the same finca.
    If lote is missing but finca exists, try to find a matching lote or set lote to None.
    """
    CacaoImage = apps.get_model('images_app', 'CacaoImage')
    Lote = apps.get_model('fincas_app', 'Lote')
    
    images = CacaoImage.objects.all()
    verified = 0
    warnings = 0
    
    for image in images:
        # If image has finca but no lote, try to find a matching lote
        if hasattr(image, 'finca') and image.finca and not image.lote:
            # Try to find a lote from the same finca
            matching_lote = Lote.objects.filter(finca=image.finca).first()
            if matching_lote:
                image.lote = matching_lote
                image.save(update_fields=['lote'])
                verified += 1
            else:
                warnings += 1
                print(f"Warning: Image {image.id} has finca {image.finca.id} but no matching lote found")
        elif hasattr(image, 'finca') and image.finca and image.lote:
            # Verify that lote.finca matches image.finca
            if image.lote.finca != image.finca:
                warnings += 1
                print(f"Warning: Image {image.id} has finca {image.finca.id} but lote {image.lote.id} belongs to finca {image.lote.finca.id}")
            else:
                verified += 1
    
    print(f"Verified {verified} images, {warnings} warnings")


def reverse_verify_and_migrate_finca_data(apps, schema_editor):
    """Reverse migration - this is a one-way migration."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('images_app', '0006_remove_cacaoimage_images_app__region_efbff0_idx_and_more'),
        ('fincas_app', '0013_normalize_lote_catalogos'),
    ]

    operations = [
        # Verify data integrity before removing field
        migrations.RunPython(
            verify_and_migrate_finca_data,
            reverse_verify_and_migrate_finca_data,
        ),
        # Remove redundant finca ForeignKey
        migrations.RemoveField(
            model_name='cacaoimage',
            name='finca',
        ),
    ]

