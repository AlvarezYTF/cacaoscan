# Generated manually - Move ReporteGenerado from api to reports app
# -*- coding: utf-8 -*-
# The table already exists as 'api_reportegenerado', so we use db_table to maintain compatibility

from django.conf import settings
from django.db import migrations, models, connection
import django.db.models.deletion


def _create_table_if_not_exists(apps, schema_editor):
    """Create table if it doesn't exist (compatible with SQLite and PostgreSQL)."""
    db_engine = connection.settings_dict.get('ENGINE', '')
    
    with connection.cursor() as cursor:
        if 'postgresql' in db_engine:
            # Check if table exists
            cursor.execute("""
                SELECT 1 FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'api_reportegenerado'
            """)
            table_exists = cursor.fetchone()
            
            if not table_exists:
                cursor.execute("""
                    CREATE TABLE api_reportegenerado (
                        id BIGSERIAL PRIMARY KEY,
                        tipo_reporte VARCHAR(20) NOT NULL,
                        formato VARCHAR(10) NOT NULL,
                        titulo VARCHAR(200) NOT NULL,
                        descripcion TEXT,
                        estado VARCHAR(20) NOT NULL DEFAULT 'generando',
                        archivo VARCHAR(100),
                        nombre_archivo VARCHAR(255),
                        tamaño_archivo INTEGER,
                        parametros JSONB DEFAULT '{}',
                        filtros_aplicados JSONB DEFAULT '{}',
                        fecha_solicitud TIMESTAMP NOT NULL,
                        fecha_generacion TIMESTAMP,
                        fecha_expiracion TIMESTAMP,
                        tiempo_generacion INTERVAL,
                        mensaje_error TEXT,
                        created_at TIMESTAMP NOT NULL,
                        updated_at TIMESTAMP NOT NULL,
                        usuario_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE
                    )
                """)
        # For SQLite, Django will handle the table creation through state operations


def _create_indexes_if_needed(apps, schema_editor):
    """Create indexes if table exists (compatible with SQLite and PostgreSQL)."""
    db_engine = connection.settings_dict.get('ENGINE', '')
    
    with connection.cursor() as cursor:
        if 'postgresql' in db_engine:
            # Check if table exists
            cursor.execute("""
                SELECT 1 FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'api_reportegenerado'
            """)
            table_exists = cursor.fetchone()
            
            if table_exists:
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS api_reporte_usuario_631114_idx 
                    ON api_reportegenerado (usuario_id, fecha_solicitud DESC)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS api_reporte_tipo_re_ac3fa0_idx 
                    ON api_reportegenerado (tipo_reporte, fecha_solicitud DESC)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS api_reporte_estado_c21744_idx 
                    ON api_reportegenerado (estado)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS api_reporte_formato_55d2b8_idx 
                    ON api_reportegenerado (formato)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS api_reporte_fecha_s_91879e_idx 
                    ON api_reportegenerado (fecha_solicitud)
                """)
        # For SQLite, Django will handle the indexes through state operations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0012_cacaoimage_metadata'),  # Depend on latest api migration
    ]

    operations = [
        # Create table if it doesn't exist (may have been created by api/migrations/0007_add_model_metrics.py)
        migrations.RunPython(
            _create_table_if_not_exists,
            migrations.RunPython.noop
        ),
        # Create indexes if they don't exist (only if table exists)
        migrations.RunPython(
            _create_indexes_if_needed,
            migrations.RunPython.noop
        ),
        # Register model in Django's state only - table already exists or was created above
        migrations.SeparateDatabaseAndState(
            state_operations=[
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
            ],
            database_operations=[
                # Table and indexes already exist (created by SQL above or by api migrations)
                # Only update Django's state, don't modify the database
                migrations.RunSQL("SELECT 1;", reverse_sql="SELECT 1;"),
            ],
        ),
    ]

