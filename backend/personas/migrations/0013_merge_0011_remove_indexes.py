# Generated manually - Merge migration for 0011_remove_duplicate_indexes and 0011_remove_redundant_indexes
# -*- coding: utf-8 -*-

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('personas', '0011_remove_duplicate_indexes'),
        ('personas', '0011_remove_redundant_indexes'),
    ]

    operations = [
        # This is a merge migration - no operations needed
        # It just merges the two branches of the migration graph
    ]


