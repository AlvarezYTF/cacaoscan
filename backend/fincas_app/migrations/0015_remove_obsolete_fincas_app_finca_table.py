# Remove obsolete fincas_app_finca table if it exists
# This table was replaced by api_finca (normalized version)
# -*- coding: utf-8 -*-
from django.db import migrations, connection


def check_and_remove_obsolete_table(apps, schema_editor):
    """
    Check if fincas_app_finca table exists and remove it if it does.
    This table is obsolete - all data should be in api_finca (normalized).
    """
    db_engine = connection.settings_dict.get('ENGINE', '')
    
    if 'postgresql' not in db_engine:
        print("Skipping table check - not PostgreSQL")
        return
    
    with connection.cursor() as cursor:
        # Check if fincas_app_finca exists
        cursor.execute("""
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'fincas_app_finca'
        """)
        old_table_exists = cursor.fetchone()
        
        # Check if api_finca exists (the normalized table)
        cursor.execute("""
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'api_finca'
        """)
        new_table_exists = cursor.fetchone()
        
        if old_table_exists:
            if new_table_exists:
                # Both tables exist - check if fincas_app_finca has data
                cursor.execute("SELECT COUNT(*) FROM fincas_app_finca")
                old_count = cursor.fetchone()[0]
                
                if old_count > 0:
                    print(f"⚠️  WARNING: fincas_app_finca table exists with {old_count} records")
                    print("   This table should be empty or data should be migrated to api_finca")
                    print("   NOT removing table automatically - manual migration may be needed")
                else:
                    # Table exists but is empty - safe to remove
                    print("Removing empty fincas_app_finca table...")
                    cursor.execute('DROP TABLE IF EXISTS fincas_app_finca CASCADE')
                    print("✅ Removed obsolete fincas_app_finca table")
            else:
                # Only old table exists - this shouldn't happen
                print("⚠️  WARNING: Only fincas_app_finca exists, api_finca does not")
                print("   This indicates a problem - NOT removing fincas_app_finca")
        else:
            print("✅ fincas_app_finca table does not exist (already cleaned up)")


def reverse_check_and_remove(apps, schema_editor):
    """Reverse migration - do nothing (one-way operation)."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('fincas_app', '0016_merge_0014_fix_indexes_and_verify'),
    ]

    operations = [
        migrations.RunPython(
            check_and_remove_obsolete_table,
            reverse_check_and_remove,
        ),
    ]

