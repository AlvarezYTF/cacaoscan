# Generated manually - Add additional fields to Finca model (altitud, tipo_suelo, clima, estado)
# -*- coding: utf-8 -*-

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fincas_app', '0006_add_string_defaults'),
    ]

    operations = [
        migrations.AddField(
            model_name='finca',
            name='altitud',
            field=models.IntegerField(default=100, help_text='Altitud en metros sobre el nivel del mar'),
        ),
        migrations.AddField(
            model_name='finca',
            name='tipo_suelo',
            field=models.CharField(default='arcilloso', help_text='Tipo de suelo de la finca', max_length=50),
        ),
        migrations.AddField(
            model_name='finca',
            name='clima',
            field=models.CharField(default='tropical', help_text='Tipo de clima de la finca', max_length=50),
        ),
        migrations.AddField(
            model_name='finca',
            name='estado',
            field=models.CharField(
                choices=[('activa', 'Activa'), ('inactiva', 'Inactiva'), ('suspendida', 'Suspendida')],
                default='activa',
                help_text='Estado de la finca',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='finca',
            name='precipitacion_anual',
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text='Precipitación anual en mm',
                max_digits=8
            ),
        ),
        migrations.AddField(
            model_name='finca',
            name='temperatura_promedio',
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text='Temperatura promedio en grados Celsius',
                max_digits=5
            ),
        ),
    ]

