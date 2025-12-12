# Generated manually - Remove duplicate CacaoImage and CacaoPrediction tables from api app
# These models are now only in images_app (images_app_cacaoimage, images_app_cacaoprediction tables)
# This migration removes the duplicate api_cacaoimage and api_cacaoprediction tables
# -*- coding: utf-8 -*-

from django.db import migrations


def check_and_drop_tables(apps, schema_editor):
    """
    Check if api_cacaoimage and api_cacaoprediction tables exist and drop them.
    Data should have been migrated to images_app_cacaoimage and images_app_cacaoprediction
    in migration images_app.0010_migrate_api_cacaoimage_data.
    """
    with schema_editor.connection.cursor() as cursor:
        # Check if api_cacaoprediction exists (drop first due to foreign key)
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'api_cacaoprediction'
            );
        """)
        prediction_table_exists = cursor.fetchone()[0]
        
        if prediction_table_exists:
            # Drop api_cacaoprediction first (it has FK to api_cacaoimage)
            cursor.execute("DROP TABLE IF EXISTS api_cacaoprediction CASCADE;")
        
        # Check if api_cacaoimage exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'api_cacaoimage'
            );
        """)
        image_table_exists = cursor.fetchone()[0]
        
        if image_table_exists:
            # Drop api_cacaoimage
            cursor.execute("DROP TABLE IF EXISTS api_cacaoimage CASCADE;")
        
        # Drop indexes if they exist
        cursor.execute("DROP INDEX IF EXISTS api_cacaoim_user_id_created_idx CASCADE;")
        cursor.execute("DROP INDEX IF EXISTS api_cacaoim_processed_idx CASCADE;")
        cursor.execute("DROP INDEX IF EXISTS api_cacaoim_region_finca_idx CASCADE;")
        cursor.execute("DROP INDEX IF EXISTS api_cacaopr_image_id_idx CASCADE;")
        cursor.execute("DROP INDEX IF EXISTS api_cacaopr_created_idx CASCADE;")
        cursor.execute("DROP INDEX IF EXISTS api_cacaopr_model_version_idx CASCADE;")


def reverse_drop_tables(apps, schema_editor):
    """
    Reverse migration: recreate api_cacaoimage and api_cacaoprediction tables.
    This is only for rollback purposes - data will not be restored.
    """
    # Note: This reverse migration recreates the table structure but does not restore data.
    # Data migration is one-way only.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_remove_duplicate_systemsettings'),
        ('images_app', '0010_migrate_api_cacaoimage_data'),  # Ensure data migration runs first
    ]

    operations = [
        migrations.RunPython(
            check_and_drop_tables,
            reverse_drop_tables,
        ),
        # Drop tables using RunSQL for cleaner output
        migrations.RunSQL(
            sql="""
                DROP TABLE IF EXISTS api_cacaoprediction CASCADE;
                DROP TABLE IF EXISTS api_cacaoimage CASCADE;
            """,
            reverse_sql="""
                -- Reverse migration: tables cannot be safely recreated without data
                -- This is a one-way migration
                SELECT 1;
            """,
        ),
    ]


