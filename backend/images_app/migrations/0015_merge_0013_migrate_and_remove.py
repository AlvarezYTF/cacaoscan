# Generated manually - Merge migration for conflicting 0013 migrations
# -*- coding: utf-8 -*-

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('images_app', '0013_migrate_image_catalogs_to_parametros'),
        ('images_app', '0014_alter_cacaoimage_metadata'),  # 0014 depends on 0013_remove, so this includes both branches
    ]

    operations = [
        # This is a merge migration - no operations needed
        # It merges the two branches of the migration graph and includes 0014
        # - 0013_migrate_image_catalogs_to_parametros
        # - 0013_remove_cacaoprediction_images_app__model_v_d66094_idx
        # - 0014_alter_cacaoimage_metadata (already applied)
    ]

