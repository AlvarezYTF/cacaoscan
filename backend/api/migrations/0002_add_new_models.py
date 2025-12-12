# Generated manually for new models
# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True)),
                ('region', models.CharField(blank=True, max_length=100, null=True)),
                ('municipality', models.CharField(blank=True, max_length=100, null=True)),
                ('farm_name', models.CharField(blank=True, max_length=200, null=True)),
                ('years_experience', models.PositiveIntegerField(blank=True, null=True)),
                ('farm_size_hectares', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('preferred_language', models.CharField(choices=[('es', 'Español'), ('en', 'English')], default='es', max_length=10)),
                ('email_notifications', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Perfil de Usuario',
                'verbose_name_plural': 'Perfiles de Usuario',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='CacaoImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='cacao_images/processed/%Y/%m/%d/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('processed', models.BooleanField(default=False)),
                ('finca', models.CharField(blank=True, max_length=200, null=True)),
                ('region', models.CharField(blank=True, max_length=100, null=True)),
                ('lote_id', models.CharField(blank=True, max_length=50, null=True)),
                ('variedad', models.CharField(blank=True, max_length=100, null=True)),
                ('fecha_cosecha', models.DateField(blank=True, null=True)),
                ('notas', models.TextField(blank=True, null=True)),
                ('file_name', models.CharField(blank=True, max_length=255, null=True)),
                ('file_size', models.PositiveIntegerField(blank=True, null=True)),
                ('file_type', models.CharField(blank=True, max_length=50, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cacao_images', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Imagen de Cacao',
                'verbose_name_plural': 'Imágenes de Cacao',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='CacaoPrediction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alto_mm', models.DecimalField(decimal_places=2, max_digits=8)),
                ('ancho_mm', models.DecimalField(decimal_places=2, max_digits=8)),
                ('grosor_mm', models.DecimalField(decimal_places=2, max_digits=8)),
                ('peso_g', models.DecimalField(decimal_places=2, max_digits=8)),
                ('confidence_alto', models.DecimalField(decimal_places=3, default=0.0, max_digits=4)),
                ('confidence_ancho', models.DecimalField(decimal_places=3, default=0.0, max_digits=4)),
                ('confidence_grosor', models.DecimalField(decimal_places=3, default=0.0, max_digits=4)),
                ('confidence_peso', models.DecimalField(decimal_places=3, default=0.0, max_digits=4)),
                ('processing_time_ms', models.PositiveIntegerField(help_text='Tiempo de procesamiento en milisegundos')),
                ('crop_url', models.URLField(blank=True, help_text='URL del crop procesado', max_length=500, null=True)),
                ('model_version', models.CharField(default='v1.0', max_length=50)),
                ('device_used', models.CharField(choices=[('cpu', 'CPU'), ('cuda', 'GPU CUDA'), ('mps', 'Apple Silicon')], default='cpu', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('image', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='prediction', to='api.cacaoimage')),
            ],
            options={
                'verbose_name': 'Predicción de Cacao',
                'verbose_name_plural': 'Predicciones de Cacao',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='cacaoimage',
            index=models.Index(fields=['user', '-created_at'], name='api_cacaoim_user_id_created_idx'),
        ),
        migrations.AddIndex(
            model_name='cacaoimage',
            index=models.Index(fields=['processed'], name='api_cacaoim_processed_idx'),
        ),
        migrations.AddIndex(
            model_name='cacaoimage',
            index=models.Index(fields=['region', 'finca'], name='api_cacaoim_region_finca_idx'),
        ),
        migrations.AddIndex(
            model_name='cacaoprediction',
            index=models.Index(fields=['image'], name='api_cacaopr_image_id_idx'),
        ),
        migrations.AddIndex(
            model_name='cacaoprediction',
            index=models.Index(fields=['-created_at'], name='api_cacaopr_created_idx'),
        ),
        migrations.AddIndex(
            model_name='cacaoprediction',
            index=models.Index(fields=['model_version'], name='api_cacaopr_model_version_idx'),
        ),
    ]


