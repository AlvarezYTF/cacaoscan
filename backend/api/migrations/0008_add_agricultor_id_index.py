# Generated manually for optimization
# Modified: Finca model was moved to fincas_app
# This migration is now a no-op because the model is in fincas_app
# -*- coding: utf-8 -*-

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_add_model_metrics'),
        ('fincas_app', '0001_initial'),  # Ensure fincas_app migrations run first
    ]

    operations = [
        # No operations - Finca model was moved to fincas_app
        # Index should be added in fincas_app migrations if needed
        migrations.RunSQL("SELECT 1;", reverse_sql="SELECT 1;"),
    ]



