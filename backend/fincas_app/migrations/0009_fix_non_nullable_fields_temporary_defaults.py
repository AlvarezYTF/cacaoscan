# Generated manually - Add temporary defaults to prevent Django prompts during makemigrations
# -*- coding: utf-8 -*-

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fincas_app', '0008_add_lote_nombre_and_additional_fields'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                # Finca fields
                migrations.AlterField(
                    model_name='finca',
                    name='nombre',
                    field=models.CharField(max_length=200, help_text='Nombre de la finca', default=''),  # Temporary
                ),
                migrations.AlterField(
                    model_name='finca',
                    name='ubicacion',
                    field=models.CharField(max_length=300, help_text='Dirección o ubicación de la finca', default=''),  # Temporary
                ),
                migrations.AlterField(
                    model_name='finca',
                    name='municipio',
                    field=models.CharField(max_length=100, help_text='Municipio donde se encuentra la finca', default=''),  # Temporary
                ),
                migrations.AlterField(
                    model_name='finca',
                    name='departamento',
                    field=models.CharField(max_length=100, help_text='Departamento donde se encuentra la finca', default=''),  # Temporary
                ),
                migrations.AlterField(
                    model_name='finca',
                    name='hectareas',
                    field=models.DecimalField(max_digits=10, decimal_places=2, help_text='Área total de la finca en hectáreas', default=0),  # Temporary
                ),
                # Lote fields
                migrations.AlterField(
                    model_name='lote',
                    name='nombre',
                    field=models.CharField(max_length=200, help_text='Nombre del lote', default=''),  # Temporary
                ),
                migrations.AlterField(
                    model_name='lote',
                    name='variedad',
                    field=models.CharField(max_length=100, help_text='Variedad de cacao del lote', default=''),  # Temporary
                ),
                migrations.AlterField(
                    model_name='lote',
                    name='area_hectareas',
                    field=models.DecimalField(max_digits=8, decimal_places=2, help_text='Área del lote en hectáreas', default=0),  # Temporary
                ),
            ],
            database_operations=[
                migrations.RunSQL("SELECT 1;", reverse_sql="SELECT 1;"),
            ],
        ),
    ]

