# Generated manually - Move ModelMetrics from api to training app
# -*- coding: utf-8 -*-
# The table already exists as 'api_modelmetrics', so we use db_table to maintain compatibility

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0012_cacaoimage_metadata'),  # Depend on latest api migration
    ]

    operations = [
        # Check if table exists before creating - use state_operations for model registration
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='ModelMetrics',
                    fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model_name', models.CharField(help_text='Nombre del modelo', max_length=100)),
                ('model_type', models.CharField(choices=[('regression', 'Modelo de Regresión'), ('classification', 'Modelo de Clasificación'), ('segmentation', 'Modelo de Segmentación'), ('incremental', 'Modelo Incremental')], max_length=20)),
                ('target', models.CharField(choices=[('alto', 'Altura'), ('ancho', 'Ancho'), ('grosor', 'Grosor'), ('peso', 'Peso'), ('calidad', 'Calidad'), ('variedad', 'Variedad')], help_text='Variable objetivo', max_length=20)),
                ('version', models.CharField(help_text='Versión del modelo', max_length=20)),
                ('metric_type', models.CharField(choices=[('training', 'Métricas de Entrenamiento'), ('validation', 'Métricas de Validación'), ('test', 'Métricas de Prueba'), ('incremental', 'Métricas Incrementales')], max_length=20)),
                ('mae', models.FloatField(help_text='Mean Absolute Error')),
                ('mse', models.FloatField(help_text='Mean Squared Error')),
                ('rmse', models.FloatField(help_text='Root Mean Squared Error')),
                ('r2_score', models.FloatField(help_text='R² Score')),
                ('mape', models.FloatField(blank=True, help_text='Mean Absolute Percentage Error', null=True)),
                ('additional_metrics', models.JSONField(default=dict, help_text='Métricas adicionales específicas del modelo')),
                ('dataset_size', models.PositiveIntegerField(help_text='Tamaño del dataset usado')),
                ('train_size', models.PositiveIntegerField(help_text='Tamaño del conjunto de entrenamiento')),
                ('validation_size', models.PositiveIntegerField(help_text='Tamaño del conjunto de validación')),
                ('test_size', models.PositiveIntegerField(help_text='Tamaño del conjunto de prueba')),
                ('epochs', models.PositiveIntegerField(help_text='Número de épocas de entrenamiento')),
                ('batch_size', models.PositiveIntegerField(help_text='Tamaño del batch')),
                ('learning_rate', models.FloatField(help_text='Tasa de aprendizaje')),
                ('model_params', models.JSONField(default=dict, help_text='Parámetros específicos del modelo')),
                ('training_time_seconds', models.PositiveIntegerField(blank=True, help_text='Tiempo de entrenamiento en segundos', null=True)),
                ('inference_time_ms', models.FloatField(blank=True, help_text='Tiempo de inferencia promedio en milisegundos', null=True)),
                ('stability_score', models.FloatField(blank=True, help_text='Puntuación de estabilidad del modelo', null=True)),
                ('knowledge_retention', models.FloatField(blank=True, help_text='Porcentaje de retención de conocimiento', null=True)),
                ('notes', models.TextField(blank=True, help_text='Notas adicionales sobre el modelo')),
                ('is_best_model', models.BooleanField(default=False, help_text='Indica si es el mejor modelo')),
                ('is_production_model', models.BooleanField(default=False, help_text='Indica si está en producción')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='model_metrics', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'api_modelmetrics',  # Maintain existing table name
                'verbose_name': 'Métricas de Modelo',
                'verbose_name_plural': 'Métricas de Modelos',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='modelmetrics',
            index=models.Index(fields=['model_name', 'version'], name='api_modelme_model_n_617b8b_idx'),
        ),
        migrations.AddIndex(
            model_name='modelmetrics',
            index=models.Index(fields=['model_type', 'target'], name='api_modelme_model_t_9928c0_idx'),
        ),
        migrations.AddIndex(
            model_name='modelmetrics',
            index=models.Index(fields=['metric_type'], name='api_modelme_metric__74fb4f_idx'),
        ),
        migrations.AddIndex(
            model_name='modelmetrics',
            index=models.Index(fields=['created_by', '-created_at'], name='api_modelme_created_5e9c32_idx'),
        ),
        migrations.AddIndex(
            model_name='modelmetrics',
            index=models.Index(fields=['is_best_model'], name='api_modelme_is_best_730ec5_idx'),
        ),
        migrations.AddIndex(
            model_name='modelmetrics',
            index=models.Index(fields=['is_production_model'], name='api_modelme_is_prod_fa489d_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='modelmetrics',
            unique_together={('model_name', 'version', 'metric_type', 'target')},
        ),
            ],
            database_operations=[
                # Table already exists (created by api/migrations/0007_add_model_metrics.py)
                # Only update Django's state, don't modify the database
                migrations.RunSQL("SELECT 1;", reverse_sql="SELECT 1;"),
            ],
        ),
    ]

