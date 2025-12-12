# Generated manually - Add default="" to all nullable string fields in Tema and Parametro
# -*- coding: utf-8 -*-
# This prevents Django from asking for one-off defaults when changing null=True to null=False

from django.db import migrations, models


def set_default_string_fields(apps, schema_editor):
    """Set empty string for null values in TextField fields."""
    Tema = apps.get_model('catalogos', 'Tema')
    Parametro = apps.get_model('catalogos', 'Parametro')
    
    # Update all nullable TextField fields to empty string
    Tema.objects.filter(descripcion__isnull=True).update(descripcion="")
    Parametro.objects.filter(descripcion__isnull=True).update(descripcion="")


def reverse_set_default_string_fields(apps, schema_editor):
    """Reverse migration - set null back."""
    Tema = apps.get_model('catalogos', 'Tema')
    Parametro = apps.get_model('catalogos', 'Parametro')
    
    # Reverse: set empty strings back to null
    Tema.objects.filter(descripcion="").update(descripcion=None)
    Parametro.objects.filter(descripcion="").update(descripcion=None)


class Migration(migrations.Migration):

    dependencies = [
        ('catalogos', '0002_departamento_municipio_and_more'),
    ]

    operations = [
        # First, set default values for existing null records
        migrations.RunPython(
            set_default_string_fields,
            reverse_set_default_string_fields
        ),
        # Then, alter all fields to add default="" and remove null=True
        migrations.AlterField(
            model_name='tema',
            name='descripcion',
            field=models.TextField(
                blank=True,
                default="",
                help_text='Descripción del tema'
            ),
        ),
        migrations.AlterField(
            model_name='parametro',
            name='descripcion',
            field=models.TextField(
                blank=True,
                default="",
                help_text='Descripción adicional del parámetro'
            ),
        ),
    ]

