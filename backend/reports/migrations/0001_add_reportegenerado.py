# Generated manually - Move ReporteGenerado from api to reports app
# The table already exists as 'api_reportegenerado', so we use db_table to maintain compatibility

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0012_cacaoimage_metadata'),  # Depend on latest api migration
    ]

    operations = [
        migrations.CreateModel(
            name='ReporteGenerado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_reporte', models.CharField(choices=[('calidad', 'Reporte de Calidad'), ('defectos', 'Reporte de Defectos'), ('rendimiento', 'Reporte de Rendimiento'), ('finca', 'Reporte de Finca'), ('lote', 'Reporte de Lote'), ('usuario', 'Reporte de Usuario'), ('auditoria', 'Reporte de Auditoría'), ('personalizado', 'Reporte Personalizado')], help_text='Tipo de reporte generado', max_length=20)),
                ('formato', models.CharField(choices=[('pdf', 'PDF'), ('excel', 'Excel'), ('csv', 'CSV'), ('json', 'JSON')], help_text='Formato del reporte', max_length=10)),
                ('titulo', models.CharField(help_text='Título del reporte', max_length=200)),
                ('descripcion', models.TextField(blank=True, help_text='Descripción del reporte', null=True)),
                ('estado', models.CharField(choices=[('generando', 'Generando'), ('completado', 'Completado'), ('fallido', 'Fallido'), ('expirado', 'Expirado')], default='generando', help_text='Estado actual del reporte', max_length=20)),
                ('archivo', models.FileField(blank=True, help_text='Archivo del reporte generado', null=True, upload_to='reportes/%Y/%m/%d/')),
                ('nombre_archivo', models.CharField(blank=True, help_text='Nombre del archivo generado', max_length=255, null=True)),
                ('tamano_archivo', models.PositiveIntegerField(blank=True, help_text='Tamaño del archivo en bytes', null=True)),
                ('parametros', models.JSONField(blank=True, default=dict, help_text='Parámetros utilizados para generar el reporte')),
                ('filtros_aplicados', models.JSONField(blank=True, default=dict, help_text='Filtros aplicados al generar el reporte')),
                ('fecha_solicitud', models.DateTimeField(auto_now_add=True, help_text='Fecha de solicitud del reporte')),
                ('fecha_generacion', models.DateTimeField(blank=True, help_text='Fecha de generación del reporte', null=True)),
                ('fecha_expiracion', models.DateTimeField(blank=True, help_text='Fecha de expiración del reporte', null=True)),
                ('tiempo_generacion', models.DurationField(blank=True, help_text='Tiempo que tardó en generarse', null=True)),
                ('mensaje_error', models.TextField(blank=True, help_text='Mensaje de error si falló la generación', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('usuario', models.ForeignKey(help_text='Usuario que solicitó el reporte', on_delete=django.db.models.deletion.CASCADE, related_name='reportes_generados', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'api_reportegenerado',  # Maintain existing table name
                'verbose_name': 'Reporte Generado',
                'verbose_name_plural': 'Reportes Generados',
                'ordering': ['-fecha_solicitud'],
            },
        ),
        migrations.AddIndex(
            model_name='reportegenerado',
            index=models.Index(fields=['usuario', '-fecha_solicitud'], name='api_reporte_usuario_631114_idx'),
        ),
        migrations.AddIndex(
            model_name='reportegenerado',
            index=models.Index(fields=['tipo_reporte', '-fecha_solicitud'], name='api_reporte_tipo_re_ac3fa0_idx'),
        ),
        migrations.AddIndex(
            model_name='reportegenerado',
            index=models.Index(fields=['estado'], name='api_reporte_estado_c21744_idx'),
        ),
        migrations.AddIndex(
            model_name='reportegenerado',
            index=models.Index(fields=['formato'], name='api_reporte_formato_55d2b8_idx'),
        ),
        migrations.AddIndex(
            model_name='reportegenerado',
            index=models.Index(fields=['fecha_solicitud'], name='api_reporte_fecha_s_91879e_idx'),
        ),
    ]

