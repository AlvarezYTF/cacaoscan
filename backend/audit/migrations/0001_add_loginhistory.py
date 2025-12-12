# Generated manually - Move LoginHistory from api to audit app
# -*- coding: utf-8 -*-
# The table already exists as 'api_loginhistory', so we use db_table to maintain compatibility

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
                    name='LoginHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField(help_text='Dirección IP del usuario')),
                ('user_agent', models.TextField(help_text='User Agent del navegador')),
                ('login_time', models.DateTimeField(auto_now_add=True, help_text='Fecha y hora del inicio de sesión')),
                ('logout_time', models.DateTimeField(blank=True, help_text='Fecha y hora del cierre de sesión', null=True)),
                ('session_duration', models.DurationField(blank=True, help_text='Duración de la sesión', null=True)),
                ('login_successful', models.BooleanField(default=True, help_text='Indica si el inicio de sesión fue exitoso')),
                ('failure_reason', models.CharField(blank=True, help_text='Razón del fallo si no fue exitoso', max_length=200, null=True)),
                ('user', models.ForeignKey(help_text='Usuario que inició sesión', on_delete=django.db.models.deletion.CASCADE, related_name='login_history', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'api_loginhistory',  # Maintain existing table name
                'verbose_name': 'Historial de Login',
                'verbose_name_plural': 'Historial de Logins',
                'ordering': ['-login_time'],
            },
        ),
        migrations.AddIndex(
            model_name='loginhistory',
            index=models.Index(fields=['user', '-login_time'], name='api_loginhi_user_id_19e442_idx'),
        ),
        migrations.AddIndex(
            model_name='loginhistory',
            index=models.Index(fields=['ip_address'], name='api_loginhi_ip_addr_8a6a17_idx'),
        ),
        migrations.AddIndex(
            model_name='loginhistory',
            index=models.Index(fields=['login_time'], name='api_loginhi_login_t_04aef5_idx'),
        ),
        migrations.AddIndex(
            model_name='loginhistory',
            index=models.Index(fields=['login_successful'], name='api_loginhi_login_s_78b423_idx'),
        ),
            ],
            database_operations=[
                # Table already exists (created by api migrations)
                # Only update Django's state, don't modify the database
                migrations.RunSQL("SELECT 1;", reverse_sql="SELECT 1;"),
            ],
        ),
    ]

