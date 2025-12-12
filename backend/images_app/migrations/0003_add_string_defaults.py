# Generated manually - Add default="" to all nullable string fields in CacaoImage
# This prevents Django from asking for one-off defaults when changing null=True to null=False

from django.db import migrations, models


def set_default_string_fields(apps, schema_editor):
    """Set empty string for null values in string fields."""
    CacaoImage = apps.get_model('images_app', 'CacaoImage')
    
    # Update all nullable string fields to empty string
    CacaoImage.objects.filter(finca_nombre__isnull=True).update(finca_nombre="")
    CacaoImage.objects.filter(region__isnull=True).update(region="")
    CacaoImage.objects.filter(variedad__isnull=True).update(variedad="")
    CacaoImage.objects.filter(notas__isnull=True).update(notas="")
    CacaoImage.objects.filter(file_name__isnull=True).update(file_name="")
    CacaoImage.objects.filter(file_type__isnull=True).update(file_type="")


def reverse_set_default_string_fields(apps, schema_editor):
    """Reverse migration - set null back."""
    CacaoImage = apps.get_model('images_app', 'CacaoImage')
    
    # Reverse: set empty strings back to null
    CacaoImage.objects.filter(finca_nombre="").update(finca_nombre=None)
    CacaoImage.objects.filter(region="").update(region=None)
    CacaoImage.objects.filter(variedad="").update(variedad=None)
    CacaoImage.objects.filter(notas="").update(notas=None)
    CacaoImage.objects.filter(file_name="").update(file_name=None)
    CacaoImage.objects.filter(file_type="").update(file_type=None)


class Migration(migrations.Migration):

    dependencies = [
        ('images_app', '0002_rename_images_app__region_8368ba_idx_images_app__region_efbff0_idx_and_more'),
    ]

    operations = [
        # First, set default values for existing null records
        migrations.RunPython(
            set_default_string_fields,
            reverse_set_default_string_fields
        ),
        # Then, alter all fields to add default="" and remove null=True
        migrations.AlterField(
            model_name='cacaoimage',
            name='finca_nombre',
            field=models.CharField(
                blank=True,
                default="",
                help_text='Nombre de la finca (campo de respaldo)',
                max_length=200
            ),
        ),
        migrations.AlterField(
            model_name='cacaoimage',
            name='region',
            field=models.CharField(
                blank=True,
                default="",
                max_length=100
            ),
        ),
        migrations.AlterField(
            model_name='cacaoimage',
            name='variedad',
            field=models.CharField(
                blank=True,
                default="",
                max_length=100
            ),
        ),
        migrations.AlterField(
            model_name='cacaoimage',
            name='notas',
            field=models.TextField(
                blank=True,
                default=""
            ),
        ),
        migrations.AlterField(
            model_name='cacaoimage',
            name='file_name',
            field=models.CharField(
                blank=True,
                default="",
                max_length=255
            ),
        ),
        migrations.AlterField(
            model_name='cacaoimage',
            name='file_type',
            field=models.CharField(
                blank=True,
                default="",
                max_length=50
            ),
        ),
    ]

