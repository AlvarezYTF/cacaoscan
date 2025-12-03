# Generated manually - Add default="" to all nullable string fields in Finca and Lote
# -*- coding: utf-8 -*-
# This prevents Django from asking for one-off defaults when changing null=True to null=False

from django.db import migrations, models


def set_default_string_fields(apps, schema_editor):
    """Set empty string for null values in TextField fields."""
    Finca = apps.get_model('fincas_app', 'Finca')
    Lote = apps.get_model('fincas_app', 'Lote')
    
    # Update all nullable TextField fields to empty string
    Finca.objects.filter(descripcion__isnull=True).update(descripcion="")
    Lote.objects.filter(descripcion__isnull=True).update(descripcion="")


def reverse_set_default_string_fields(apps, schema_editor):
    """Reverse migration - set null back."""
    Finca = apps.get_model('fincas_app', 'Finca')
    Lote = apps.get_model('fincas_app', 'Lote')
    
    # Reverse: set empty strings back to null
    Finca.objects.filter(descripcion="").update(descripcion=None)
    Lote.objects.filter(descripcion="").update(descripcion=None)


class Migration(migrations.Migration):

    dependencies = [
        ('fincas_app', '0005_rename_fincas_app__agricul_396b5b_idx_api_finca_agricul_f9cee8_idx_and_more'),
    ]

    operations = [
        # First, set default values for existing null records
        migrations.RunPython(
            set_default_string_fields,
            reverse_set_default_string_fields
        ),
        # Then, alter all fields to add default="" and remove null=True
        migrations.AlterField(
            model_name='finca',
            name='descripcion',
            field=models.TextField(
                blank=True,
                default="",
                help_text='Descripción adicional de la finca'
            ),
        ),
        migrations.AlterField(
            model_name='lote',
            name='descripcion',
            field=models.TextField(
                blank=True,
                default="",
                help_text='Descripción adicional del lote'
            ),
        ),
    ]

