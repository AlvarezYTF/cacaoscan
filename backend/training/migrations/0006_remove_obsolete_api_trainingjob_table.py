# Remove obsolete api_trainingjob table if it exists
# This table was replaced by training_trainingjob (normalized version)
# -*- coding: utf-8 -*-
from django.db import migrations, connection


def check_and_remove_obsolete_table(apps, schema_editor):
    """
    Check if api_trainingjob table exists and remove it if it does.
    This table is obsolete - all data should be in training_trainingjob (normalized).
    """
    db_engine = connection.settings_dict.get('ENGINE', '')
    
    if 'postgresql' not in db_engine:
        print("Skipping table check - not PostgreSQL")
        return
    
    with connection.cursor() as cursor:
        # Check if api_trainingjob exists
        cursor.execute("""
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'api_trainingjob'
        """)
        old_table_exists = cursor.fetchone()
        
        # Check if training_trainingjob exists (the normalized table)
        cursor.execute("""
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'training_trainingjob'
        """)
        new_table_exists = cursor.fetchone()
        
        if old_table_exists:
            if new_table_exists:
                # Both tables exist - check if api_trainingjob has data
                cursor.execute("SELECT COUNT(*) FROM api_trainingjob")
                old_count = cursor.fetchone()[0]
                
                if old_count > 0:
                    print(f"⚠️  WARNING: api_trainingjob table exists with {old_count} records")
                    print("   This table should be empty or data should be migrated to training_trainingjob")
                    print("   NOT removing table automatically - manual migration may be needed")
                    print("   To migrate data manually:")
                    print("   1. Copy data from api_trainingjob to training_trainingjob")
                    print("   2. Verify data integrity")
                    print("   3. Drop api_trainingjob table manually")
                else:
                    # Table exists but is empty - safe to remove
                    print("Removing empty api_trainingjob table...")
                    cursor.execute('DROP TABLE IF EXISTS api_trainingjob CASCADE')
                    print("✅ Removed obsolete api_trainingjob table")
            else:
                # Only old table exists - this shouldn't happen
                print("⚠️  WARNING: Only api_trainingjob exists, training_trainingjob does not")
                print("   This indicates a problem - NOT removing api_trainingjob")
        else:
            print("✅ api_trainingjob table does not exist (already cleaned up)")


def reverse_check_and_remove(apps, schema_editor):
    """Reverse migration - do nothing (one-way operation)."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0005_alter_modelmetrics_batch_size_and_more'),
    ]

    operations = [
        migrations.RunPython(
            check_and_remove_obsolete_table,
            reverse_check_and_remove,
        ),
    ]


