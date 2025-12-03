# Generated manually - Add temporary defaults to prevent Django prompts during makemigrations
# -*- coding: utf-8 -*-

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0003_alter_trainingjob_model_path'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                # TrainingJob fields
                migrations.AlterField(
                    model_name='trainingjob',
                    name='job_id',
                    field=models.CharField(max_length=100, unique=True, help_text='ID único del trabajo', default=''),  # Temporary
                ),
                migrations.AlterField(
                    model_name='trainingjob',
                    name='job_type',
                    field=models.CharField(max_length=20, choices=[('regression', 'Modelo de Regresión'), ('vision', 'Modelo de Visión (YOLOv8)'), ('incremental', 'Entrenamiento Incremental')], default='regression'),  # Temporary
                ),
                migrations.AlterField(
                    model_name='trainingjob',
                    name='model_name',
                    field=models.CharField(max_length=100, help_text='Nombre del modelo a entrenar', default=''),  # Temporary
                ),
                migrations.AlterField(
                    model_name='trainingjob',
                    name='dataset_size',
                    field=models.PositiveIntegerField(help_text='Número de imágenes en el dataset', default=0),  # Temporary
                ),
                # ModelMetrics fields
                migrations.AlterField(
                    model_name='modelmetrics',
                    name='model_name',
                    field=models.CharField(max_length=100, default=''),  # Temporary
                ),
                migrations.AlterField(
                    model_name='modelmetrics',
                    name='model_type',
                    field=models.CharField(max_length=20, choices=[('regression', 'Modelo de Regresión'), ('classification', 'Modelo de Clasificación'), ('segmentation', 'Modelo de Segmentación'), ('incremental', 'Modelo Incremental')], default='regression'),  # Temporary
                ),
                migrations.AlterField(
                    model_name='modelmetrics',
                    name='target',
                    field=models.CharField(max_length=20, choices=[('alto', 'Altura'), ('ancho', 'Ancho'), ('grosor', 'Grosor'), ('peso', 'Peso'), ('calidad', 'Calidad'), ('variedad', 'Variedad')], default='alto'),  # Temporary
                ),
                migrations.AlterField(
                    model_name='modelmetrics',
                    name='version',
                    field=models.CharField(max_length=20, default='v1.0'),  # Temporary
                ),
                migrations.AlterField(
                    model_name='modelmetrics',
                    name='metric_type',
                    field=models.CharField(max_length=20, choices=[('training', 'Métricas de Entrenamiento'), ('validation', 'Métricas de Validación'), ('test', 'Métricas de Prueba'), ('incremental', 'Métricas Incrementales')], default='training'),  # Temporary
                ),
                migrations.AlterField(
                    model_name='modelmetrics',
                    name='mae',
                    field=models.FloatField(default=0.0),  # Temporary
                ),
                migrations.AlterField(
                    model_name='modelmetrics',
                    name='mse',
                    field=models.FloatField(default=0.0),  # Temporary
                ),
                migrations.AlterField(
                    model_name='modelmetrics',
                    name='rmse',
                    field=models.FloatField(default=0.0),  # Temporary
                ),
                migrations.AlterField(
                    model_name='modelmetrics',
                    name='r2_score',
                    field=models.FloatField(default=0.0),  # Temporary
                ),
                migrations.AlterField(
                    model_name='modelmetrics',
                    name='dataset_size',
                    field=models.PositiveIntegerField(default=0),  # Temporary
                ),
                migrations.AlterField(
                    model_name='modelmetrics',
                    name='train_size',
                    field=models.PositiveIntegerField(default=0),  # Temporary
                ),
                migrations.AlterField(
                    model_name='modelmetrics',
                    name='validation_size',
                    field=models.PositiveIntegerField(default=0),  # Temporary
                ),
                migrations.AlterField(
                    model_name='modelmetrics',
                    name='test_size',
                    field=models.PositiveIntegerField(default=0),  # Temporary
                ),
                migrations.AlterField(
                    model_name='modelmetrics',
                    name='epochs',
                    field=models.PositiveIntegerField(default=0),  # Temporary
                ),
                migrations.AlterField(
                    model_name='modelmetrics',
                    name='batch_size',
                    field=models.PositiveIntegerField(default=0),  # Temporary
                ),
                migrations.AlterField(
                    model_name='modelmetrics',
                    name='learning_rate',
                    field=models.FloatField(default=0.001),  # Temporary
                ),
            ],
            database_operations=[
                migrations.RunSQL("SELECT 1;", reverse_sql="SELECT 1;"),
            ],
        ),
    ]

