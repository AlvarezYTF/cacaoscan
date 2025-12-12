# Generated manually - Force remove old catalog tables
# This migration ensures old catalog tables are removed even if 0014 didn't execute properly
# -*- coding: utf-8 -*-

from django.db import migrations


def force_remove_old_catalog_tables(apps, schema_editor):
    """
    Force removal of old catalog tables.
    This migration is a safety net in case 0014 didn't execute properly.
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
                quoted_table_name = schema_editor.connection.ops.quote_name(table_name)
                cursor.execute(f"SELECT COUNT(*) FROM {quoted_table_name};")
                count = cursor.fetchone()[0]
                
                if count > 0:
                    print(f"INFO: Table {table_name} has {count} records.")
                    print(f"  Data should have been migrated to catalogos_parametro.")
                    print(f"  Proceeding with table deletion (data is preserved in catalogos_parametro).")
                
                # Drop table with CASCADE to remove all constraints
                quoted_table_name = schema_editor.connection.ops.quote_name(table_name)
                try:
                    cursor.execute(f"DROP TABLE IF EXISTS {quoted_table_name} CASCADE;")
                    print(f"✓ Dropped table: {table_name}")
                except Exception as e:
                    print(f"ERROR: Could not drop table {table_name}: {e}")
                    print(f"  This may be due to remaining foreign key constraints.")
                    print(f"  Please verify that all FKs have been migrated to catalogos_parametro.")
                    # Don't raise - continue with other tables
            else:
                print(f"Table {table_name} does not exist, skipping")


def reverse_force_remove_old_catalog_tables(apps, schema_editor):
    """
    Reverse migration: This cannot recreate the old tables.
    """
    print("WARNING: Reverse migration not supported - old catalog tables cannot be recreated")


class Migration(migrations.Migration):

    dependencies = [
        ('catalogos', '0014_remove_old_catalog_tables'),
    ]

    operations = [
        migrations.RunPython(
            force_remove_old_catalog_tables,
            reverse_force_remove_old_catalog_tables,
        ),
    ]

