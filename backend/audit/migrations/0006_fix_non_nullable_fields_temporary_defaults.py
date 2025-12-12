# Generated manually - Add temporary defaults to prevent Django prompts during makemigrations
# -*- coding: utf-8 -*-

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audit', '0005_migrate_activitylog_fields'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name='activitylog',
                    name='action',
                    field=models.CharField(max_length=100, help_text='Acción realizada', default=''),  # Temporary
                ),
            ],
            database_operations=[
                migrations.RunSQL("SELECT 1;", reverse_sql="SELECT 1;"),
            ],
        ),
    ]

