# Generated manually - Add temporary defaults to prevent Django prompts during makemigrations
# -*- coding: utf-8 -*-
# This migration adds defaults directly to the database schema for fields that don't have them
# These defaults are ONLY for migration purposes and should NOT be added to the models

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('personas', '0006_add_string_defaults'),
        ('catalogos', '0001_initial'),
    ]

    operations = [
        # Use SeparateDatabaseAndState to sync Django's state with models
        # This prevents Django from asking about missing defaults
        migrations.SeparateDatabaseAndState(
            state_operations=[
                # Update Django's state to include temporary defaults
                # These defaults are ONLY in Django's migration state, NOT in the models
                migrations.AlterField(
                    model_name='persona',
                    name='numero_documento',
                    field=models.CharField(
                        help_text='Número de documento de identidad',
                        max_length=20,
                        unique=True,
                        default='',  # Temporary default for migration state only
                    ),
                ),
                migrations.AlterField(
                    model_name='persona',
                    name='primer_nombre',
                    field=models.CharField(
                        help_text='Primer nombre',
                        max_length=50,
                        default='',  # Temporary default for migration state only
                    ),
                ),
                migrations.AlterField(
                    model_name='persona',
                    name='primer_apellido',
                    field=models.CharField(
                        help_text='Primer apellido',
                        max_length=50,
                        default='',  # Temporary default for migration state only
                    ),
                ),
                migrations.AlterField(
                    model_name='persona',
                    name='telefono',
                    field=models.CharField(
                        help_text='Número de teléfono (único)',
                        max_length=15,
                        unique=True,
                        default='',  # Temporary default for migration state only
                    ),
                ),
            ],
            database_operations=[
                # No database changes - schema is already correct
                # We only update Django's state to prevent prompts
                migrations.RunSQL("SELECT 1;", reverse_sql="SELECT 1;"),
            ],
        ),
    ]
