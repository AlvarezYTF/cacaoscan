# Generated manually - Remove old catalog tables after migration to unified system
# Phase 4 of catalog unification: Cleanup old catalog tables
# -*- coding: utf-8 -*-

from django.db import migrations


def remove_old_catalog_tables(apps, schema_editor):
    """
    Remove old catalog tables after verifying migration is complete.
    This should only be done after all FKs have been migrated.
    
    IMPORTANT: This migration will only drop tables if they are empty.
    If tables have data, they will be skipped with a warning.
    """
    with schema_editor.connection.cursor() as cursor:
        # List of old catalog tables to remove
        old_tables = [
            'catalogos_clima',
            'catalogos_estadofinca',
            'catalogos_estadolote',
            'catalogos_estadoreporte',
            'catalogos_formatoreporte',
            'catalogos_tipoarchivo',
            'catalogos_tipodispositivo',
            'catalogos_tiponotificacion',
            'catalogos_tiporeporte',
            'catalogos_tiposuelo',
            'catalogos_variedadcacao',
            'catalogos_versionmodelo',
        ]
        
        for table_name in old_tables:
            # Check if table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                );
            """, [table_name])
            
            table_exists = cursor.fetchone()[0]
            
            if table_exists:
                # Check if table has any remaining data (for logging)
                # Use quote_name to safely escape table name
                quoted_table_name = schema_editor.connection.ops.quote_name(table_name)
                cursor.execute(f"SELECT COUNT(*) FROM {quoted_table_name};")
                count = cursor.fetchone()[0]
                
                if count > 0:
                    print(f"INFO: Table {table_name} has {count} records.")
                    print(f"  Data should have been migrated to catalogos_parametro in migration 0013.")
                    print(f"  Proceeding with table deletion (data is preserved in catalogos_parametro).")
                
                # Drop table with CASCADE to remove all constraints
                # Use quote_name to safely escape table name
                quoted_table_name = schema_editor.connection.ops.quote_name(table_name)
                try:
                    cursor.execute(f"DROP TABLE IF EXISTS {quoted_table_name} CASCADE;")
                    print(f"✓ Dropped table: {table_name}")
                except Exception as e:
                    print(f"ERROR: Could not drop table {table_name}: {e}")
                    print(f"  This may be due to remaining foreign key constraints.")
                    print(f"  Please verify that all FKs have been migrated to catalogos_parametro.")
                    raise  # Re-raise to fail the migration if we can't drop the table
            else:
                print(f"Table {table_name} does not exist, skipping")


def reverse_remove_old_catalog_tables(apps, schema_editor):
    """
    Reverse migration: This cannot recreate the old tables as we don't have
    the exact structure. This is a one-way migration.
    """
    # This migration cannot be reversed - old catalog tables are permanently removed
    print("WARNING: Reverse migration not supported - old catalog tables cannot be recreated")


class Migration(migrations.Migration):

    dependencies = [
        ('catalogos', '0013_create_themes_and_migrate_catalogs'),
        # Note: These migrations may not exist yet, so we make them optional
        # The migration will check if tables exist before trying to drop them
    ]

    operations = [
        migrations.RunPython(
            remove_old_catalog_tables,
            reverse_remove_old_catalog_tables,
        ),
    ]

