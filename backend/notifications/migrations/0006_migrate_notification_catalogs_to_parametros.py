# Generated manually - Migrate Notification catalog FK to Parametro
# Phase 2 of catalog unification: Update Foreign Keys in notifications
# -*- coding: utf-8 -*-

from django.db import migrations, models
import django.db.models.deletion


def migrate_notification_catalogs_to_parametros(apps, schema_editor):
    """
    Migrate Notification catalog ForeignKey to Parametro.
    Updates: tipo
    """
    Notification = apps.get_model('notifications', 'Notification')
    Parametro = apps.get_model('catalogos', 'Parametro')
    Tema = apps.get_model('catalogos', 'Tema')
    
    # Get theme
    tema_tipo_notificacion = Tema.objects.get(codigo='TEMA_TIPO_NOTIFICACION')
    
    # Mapping function
    def get_parametro_by_catalog_id(tema, old_catalog_id, catalog_model_name):
        """Get parametro by old catalog ID."""
        if not old_catalog_id:
            return None
        
        try:
            CatalogModel = apps.get_model('catalogos', catalog_model_name)
            old_record = CatalogModel.objects.get(id=old_catalog_id)
            parametro = Parametro.objects.get(tema=tema, codigo=old_record.codigo)
            return parametro
        except (CatalogModel.DoesNotExist, Parametro.DoesNotExist):
            print(f"Warning: Could not find parametro for {catalog_model_name} id={old_catalog_id}")
            return None
    
    # Migrate tipo
    notifications = Notification.objects.exclude(tipo__isnull=True)
    migrated_tipo = 0
    for notification in notifications:
        parametro = get_parametro_by_catalog_id(tema_tipo_notificacion, notification.tipo_id, 'TipoNotificacion')
        if parametro:
            notification.tipo_parametro_id = parametro.id
            migrated_tipo += 1
    Notification.objects.bulk_update(notifications, ['tipo_parametro_id'])
    print(f"Migrated {migrated_tipo} tipo references")


def reverse_migrate_notification_catalogs(apps, schema_editor):
    """Reverse migration - not fully supported."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0005_normalize_notification_tipo'),
        ('catalogos', '0013_create_themes_and_migrate_catalogs'),
    ]

    operations = [
        # Add temporary column
        migrations.AddField(
            model_name='notification',
            name='tipo_parametro',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=models.PROTECT,
                related_name='notifications_tipo_temp',
                to='catalogos.parametro',
                help_text='Tipo de notificación (temporal - migración)'
            ),
        ),
        # Migrate data
        migrations.RunPython(
            migrate_notification_catalogs_to_parametros,
            reverse_migrate_notification_catalogs,
        ),
        # Remove old FK
        migrations.RemoveField(
            model_name='notification',
            name='tipo',
        ),
        # Rename temporary column
        migrations.RenameField(
            model_name='notification',
            old_name='tipo_parametro',
            new_name='tipo',
        ),
        # Update FK definition
        migrations.AlterField(
            model_name='notification',
            name='tipo',
            field=models.ForeignKey(
                on_delete=models.PROTECT,
                related_name='notifications',
                to='catalogos.parametro',
                help_text='Tipo de notificación (normalizado con catálogo)'
            ),
        ),
    ]

