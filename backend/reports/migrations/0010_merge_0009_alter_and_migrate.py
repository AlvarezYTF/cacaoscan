# Generated manually - Merge migration for conflicting 0009 migrations
# -*- coding: utf-8 -*-

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0009_alter_reportegenerado_filtros_aplicados_and_more'),
        ('reports', '0009_migrate_report_catalogs_to_parametros'),
    ]

    operations = [
        # This is a merge migration - no operations needed
        # It just merges the two branches of the migration graph:
        # - 0009_alter_reportegenerado_filtros_aplicados_and_more
        # - 0009_migrate_report_catalogs_to_parametros
    ]


