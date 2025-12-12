# Generated migration to normalize Notification.tipo using TipoNotificacion catalog (3NF)
# -*- coding: utf-8 -*-
from django.db import migrations, models
import django.db.models.deletion


def migrate_tipo_to_catalog(apps, schema_editor):
    """
    Migrate Notification.tipo from CharField to ForeignKey to Parametro.
    Maps old choice values to Parametro codigos (TEMA_TIPO_NOTIFICACION).
    """
    from django.db import connection
    
    Notification = apps.get_model('notifications', 'Notification')
    Parametro = apps.get_model('catalogos', 'Parametro')
    Tema = apps.get_model('catalogos', 'Tema')
    
    # Get theme
    try:
        tema_tipo_notificacion = Tema.objects.get(codigo='TEMA_TIPO_NOTIFICACION')
    except Tema.DoesNotExist:
        print("WARNING: TEMA_TIPO_NOTIFICACION not found. Skipping Notification tipo migration.")
        return
    
    # Mapping from old choice values to new codigos
    tipo_mapping = {
        'info': 'INFO',
        'warning': 'WARNING',
        'error': 'ERROR',
        'success': 'SUCCESS',
        'defect_alert': 'DEFECT_ALERT',
        'report_ready': 'REPORT_READY',
        'training_complete': 'TRAINING_COMPLETE',
        'welcome': 'WELCOME',
    }
    
    # Use raw SQL to read old tipo values and update
    with connection.cursor() as cursor:
        # Get all notifications with their old tipo values
        cursor.execute("SELECT id, tipo FROM notifications_notification")
        rows = cursor.fetchall()
        
        migrated = 0
        skipped = 0
        
        for notification_id, old_tipo in rows:
            if not old_tipo:
                old_tipo = 'info'  # Default
            
            codigo = tipo_mapping.get(old_tipo, 'INFO')
            
            try:
                parametro = Parametro.objects.get(tema=tema_tipo_notificacion, codigo=codigo)
                # Update using raw SQL to set tipo_id
                cursor.execute(
                    "UPDATE notifications_notification SET tipo_id = %s WHERE id = %s",
                    [parametro.id, notification_id]
                )
                migrated += 1
            except Parametro.DoesNotExist:
                skipped += 1
                print(f"Warning: Parametro (TEMA_TIPO_NOTIFICACION) with codigo '{codigo}' not found for notification {notification_id}")
        
        print(f"Migrated {migrated} notifications, skipped {skipped} notifications")


def reverse_migrate_tipo_to_charfield(apps, schema_editor):
    """
    Reverse migration: populate tipo CharField from tipo ForeignKey.
    """
    from django.db import connection
    
    Notification = apps.get_model('notifications', 'Notification')
    
    # Reverse mapping from codigos to old choice values
    codigo_mapping = {
        'INFO': 'info',
        'WARNING': 'warning',
        'ERROR': 'error',
        'SUCCESS': 'success',
        'DEFECT_ALERT': 'defect_alert',
        'REPORT_READY': 'report_ready',
        'TRAINING_COMPLETE': 'training_complete',
        'WELCOME': 'welcome',
    }
    
    # Use raw SQL to read tipo_id and update tipo CharField
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT n.id, tn.codigo 
            FROM notifications_notification n
            JOIN catalogos_tiponotificacion tn ON n.tipo_id = tn.id
        """)
        rows = cursor.fetchall()
        
        for notification_id, codigo in rows:
            old_value = codigo_mapping.get(codigo, 'info')
            cursor.execute(
                "UPDATE notifications_notification SET tipo = %s WHERE id = %s",
                [old_value, notification_id]
            )


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0003_alter_notification_mensaje_alter_notification_titulo'),
        ('catalogos', '0013_create_themes_and_migrate_catalogs'),  # Use unified catalog system
    ]

    operations = [
        # Add new ForeignKey field (nullable initially)
        migrations.AddField(
            model_name='notification',
            name='tipo_new',
            field=models.ForeignKey(
                blank=True,
                help_text='Tipo de notificación (normalizado con catálogo)',
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='notifications_new',
                to='catalogos.parametro',
                limit_choices_to={'tema__codigo': 'TEMA_TIPO_NOTIFICACION'}
            ),
        ),
        # Migrate data from tipo CharField to tipo_new ForeignKey
        migrations.RunPython(
            migrate_tipo_to_catalog,
            reverse_migrate_tipo_to_charfield,
        ),
        # Remove old CharField
        migrations.RemoveField(
            model_name='notification',
            name='tipo',
        ),
        # Rename tipo_new to tipo
        migrations.RenameField(
            model_name='notification',
            old_name='tipo_new',
            new_name='tipo',
        ),
        # Make tipo non-nullable
        migrations.AlterField(
            model_name='notification',
            name='tipo',
            field=models.ForeignKey(
                help_text='Tipo de notificación (normalizado con catálogo)',
                on_delete=django.db.models.deletion.PROTECT,
                related_name='notifications',
                to='catalogos.parametro',
                limit_choices_to={'tema__codigo': 'TEMA_TIPO_NOTIFICACION'}
            ),
        ),
        # Add index
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['tipo'], name='notificati_tipo_id_idx'),
        ),
    ]

