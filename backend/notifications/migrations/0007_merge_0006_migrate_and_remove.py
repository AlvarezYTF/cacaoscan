# Generated manually - Merge migration for conflicting 0006 migrations
# -*- coding: utf-8 -*-

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0006_migrate_notification_catalogs_to_parametros'),
        ('notifications', '0006_remove_notification_notificati_tipo_id_idx'),
    ]

    operations = [
        # This is a merge migration - no operations needed
        # It just merges the two branches of the migration graph:
        # - 0006_migrate_notification_catalogs_to_parametros
        # - 0006_remove_notification_notificati_tipo_id_idx
    ]


