# Generated manually - Create ActivityLog model with all fields
# -*- coding: utf-8 -*-
# The table already exists as 'api_activitylog', so we use db_table to maintain compatibility

from django.conf import settings
from django.db import migrations, models, connection
import django.db.models.deletion


def _add_action_field_if_needed(apps, schema_editor):
    """Add action field if it doesn't exist (compatible with SQLite and PostgreSQL)."""
    db_engine = connection.settings_dict.get('ENGINE', '')
    
    with connection.cursor() as cursor:
        if 'postgresql' in db_engine:
            # Check if action field exists
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'api_activitylog' AND column_name = 'action'
            """)
            action_exists = cursor.fetchone()
            
            if not action_exists:
                # Check if accion exists
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'api_activitylog' AND column_name = 'accion'
                """)
                accion_exists = cursor.fetchone()
                
                if not accion_exists:
                    # Neither exists, add action with default
                    cursor.execute("""
                        ALTER TABLE api_activitylog 
                        ADD COLUMN action VARCHAR(100) DEFAULT 'unknown' NOT NULL
                    """)
                    cursor.execute("""
                        ALTER TABLE api_activitylog 
                        ALTER COLUMN action DROP DEFAULT
                    """)
        # For SQLite, Django will handle the field creation through state operations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('audit', '0001_add_loginhistory'),
    ]

    operations = [
        # Use SeparateDatabaseAndState because the table already exists
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='ActivityLog',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('user', models.ForeignKey(
                            help_text='Usuario que realizó la acción',
                            on_delete=django.db.models.deletion.CASCADE,
                            related_name='activity_logs',
                            to=settings.AUTH_USER_MODEL
                        )),
                        ('action', models.CharField(help_text='Acción realizada', max_length=100)),
                        ('resource_type', models.CharField(blank=True, default='', help_text='Tipo de recurso afectado', max_length=50)),
                        ('resource_id', models.IntegerField(blank=True, help_text='ID del recurso afectado', null=True)),
                        ('details', models.JSONField(blank=True, default=dict, help_text='Detalles adicionales de la acción')),
                        ('ip_address', models.GenericIPAddressField(blank=True, help_text='Dirección IP del usuario', null=True)),
                        ('user_agent', models.TextField(blank=True, default='', help_text='User Agent del navegador')),
                        ('timestamp', models.DateTimeField(auto_now_add=True, help_text='Fecha y hora de la acción')),
                    ],
                    options={
                        'db_table': 'api_activitylog',
                        'verbose_name': 'Log de Actividad',
                        'verbose_name_plural': 'Logs de Actividad',
                        'ordering': ['-timestamp'],
                    },
                ),
                migrations.AddIndex(
                    model_name='activitylog',
                    index=models.Index(fields=['user', '-timestamp'], name='api_activit_user_id_timestamp_idx'),
                ),
                migrations.AddIndex(
                    model_name='activitylog',
                    index=models.Index(fields=['action'], name='api_activit_action_idx'),
                ),
                migrations.AddIndex(
                    model_name='activitylog',
                    index=models.Index(fields=['resource_type', 'resource_id'], name='api_activit_resource_idx'),
                ),
            ],
            database_operations=[
                # Table already exists (created by api migrations)
                # Add action field if it doesn't exist (will be renamed from accion in migration 0005)
                migrations.RunPython(
                    _add_action_field_if_needed,
                    migrations.RunPython.noop
                ),
            ],
        ),
    ]
