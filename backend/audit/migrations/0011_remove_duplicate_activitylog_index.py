# Generated manually - Remove duplicate index on ActivityLog
# The index api_activit_usuario_c881c3_idx is identical to api_activit_user_id_7d2450_idx
# Both index (user_id, timestamp DESC), so one is redundant
# -*- coding: utf-8 -*-

from django.db import migrations


def remove_duplicate_index(apps, schema_editor):
    """
    Remove the duplicate index api_activit_usuario_c881c3_idx.
    This index was created on the old 'usuario' field which was renamed to 'user',
    but the index still exists and is identical to api_activit_user_id_7d2450_idx.
    """
    connection = schema_editor.connection
    
    with connection.cursor() as cursor:
        # Check if the duplicate index exists
        cursor.execute("""
            SELECT 1 FROM pg_indexes 
            WHERE tablename = 'api_activitylog' 
            AND indexname = 'api_activit_usuario_c881c3_idx'
        """)
        
        if cursor.fetchone():
            # Drop the duplicate index
            cursor.execute('DROP INDEX IF EXISTS "api_activit_usuario_c881c3_idx"')
            print("Removed duplicate index: api_activit_usuario_c881c3_idx")


def reverse_remove_duplicate_index(apps, schema_editor):
    """
    Reverse migration: recreate the index (not typically needed, but included for completeness).
    Note: This would recreate a duplicate index, so it's not recommended to use.
    """
    connection = schema_editor.connection
    
    with connection.cursor() as cursor:
        # Check if the index doesn't exist
        cursor.execute("""
            SELECT 1 FROM pg_indexes 
            WHERE tablename = 'api_activitylog' 
            AND indexname = 'api_activit_usuario_c881c3_idx'
        """)
        
        if not cursor.fetchone():
            # Recreate the index (though it's a duplicate)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS api_activit_usuario_c881c3_idx 
                ON api_activitylog (user_id, timestamp DESC)
            """)


class Migration(migrations.Migration):

    dependencies = [
        ('audit', '0010_rename_api_activity_content_idx_api_activit_content_e169d7_idx_and_more'),
    ]

    operations = [
        migrations.RunPython(
            remove_duplicate_index,
            reverse_remove_duplicate_index,
        ),
    ]


