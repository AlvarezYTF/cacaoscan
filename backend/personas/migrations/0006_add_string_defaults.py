# Generated manually - Add default="" to all nullable string fields in Persona
# -*- coding: utf-8 -*-
# This prevents Django from asking for one-off defaults when changing null=True to null=False

from django.db import migrations, models


def set_default_string_fields(apps, schema_editor):
    """Set empty string for null values in string fields."""
    Persona = apps.get_model('personas', 'Persona')
    
    # Update all nullable string fields to empty string
    Persona.objects.filter(segundo_nombre__isnull=True).update(segundo_nombre="")
    Persona.objects.filter(segundo_apellido__isnull=True).update(segundo_apellido="")
    Persona.objects.filter(direccion__isnull=True).update(direccion="")


def reverse_set_default_string_fields(apps, schema_editor):
    """Reverse migration - set null back."""
    Persona = apps.get_model('personas', 'Persona')
    
    # Reverse: set empty strings back to null
    Persona.objects.filter(segundo_nombre="").update(segundo_nombre=None)
    Persona.objects.filter(segundo_apellido="").update(segundo_apellido=None)
    Persona.objects.filter(direccion="").update(direccion=None)


class Migration(migrations.Migration):

    dependencies = [
        ('personas', '0005_merge_20251029_2301'),
    ]

    operations = [
        # First, set default values for existing null records
        migrations.RunPython(
            set_default_string_fields,
            reverse_set_default_string_fields
        ),
        # Then, alter all fields to add default="" and remove null=True
        migrations.AlterField(
            model_name='persona',
            name='segundo_nombre',
            field=models.CharField(
                blank=True,
                default="",
                help_text='Segundo nombre (opcional)',
                max_length=50
            ),
        ),
        migrations.AlterField(
            model_name='persona',
            name='segundo_apellido',
            field=models.CharField(
                blank=True,
                default="",
                help_text='Segundo apellido (opcional)',
                max_length=50
            ),
        ),
        migrations.AlterField(
            model_name='persona',
            name='direccion',
            field=models.CharField(
                blank=True,
                default="",
                help_text='Dirección de residencia',
                max_length=255
            ),
        ),
    ]

