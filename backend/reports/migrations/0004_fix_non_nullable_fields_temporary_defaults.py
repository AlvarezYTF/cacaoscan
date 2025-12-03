# Generated manually - Add temporary defaults to prevent Django prompts during makemigrations
# -*- coding: utf-8 -*-

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0003_add_string_defaults'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name='reportegenerado',
                    name='tipo_reporte',
                    field=models.CharField(
                        max_length=20,
                        choices=[('calidad', 'Reporte de Calidad'), ('defectos', 'Reporte de Defectos'), ('rendimiento', 'Reporte de Rendimiento'), ('finca', 'Reporte de Finca'), ('lote', 'Reporte de Lote'), ('usuario', 'Reporte de Usuario'), ('auditoria', 'Reporte de Auditoría'), ('personalizado', 'Reporte Personalizado'), ('analisis_periodo', 'Análisis por Período')],
                        default='calidad',  # Temporary default for migration state only
                    ),
                ),
            ],
            database_operations=[
                migrations.RunSQL("SELECT 1;", reverse_sql="SELECT 1;"),
            ],
        ),
    ]

