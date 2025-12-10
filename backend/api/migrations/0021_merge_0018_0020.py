# Generated manually - Merge migration for 0018_remove_api_emailverificationtoken_table and 0020_migrate_and_remove_duplicate_userprofile
# -*- coding: utf-8 -*-

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0018_remove_api_emailverificationtoken_table'),
        ('api', '0020_migrate_and_remove_duplicate_userprofile'),
    ]

    operations = [
        # This is a merge migration - no operations needed
        # It just merges the two branches of the migration graph:
        # - 0018_remove_api_emailverificationtoken_table (removes duplicate EmailVerificationToken table)
        # - 0020_migrate_and_remove_duplicate_userprofile (removes duplicate UserProfile table)
    ]

