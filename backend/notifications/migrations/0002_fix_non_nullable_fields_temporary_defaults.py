# Generated manually - Add temporary defaults to prevent Django prompts during makemigrations
# -*- coding: utf-8 -*-

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name='notification',
                    name='titulo',
                    field=models.CharField(max_length=200, help_text='Título de la notificación', default=''),  # Temporary
                ),
                migrations.AlterField(
                    model_name='notification',
                    name='mensaje',
                    field=models.TextField(help_text='Mensaje detallado de la notificación', default=''),  # Temporary
                ),
            ],
            database_operations=[
                migrations.RunSQL("SELECT 1;", reverse_sql="SELECT 1;"),
            ],
        ),
    ]

