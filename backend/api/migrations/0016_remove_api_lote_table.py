# Generated manually - Remove api_lote table from database
# This table was created in migration 0004 but the model was moved to fincas_app
# The table api_lote is now obsolete and should be removed
# -*- coding: utf-8 -*-

from django.db import migrations


def drop_api_lote_table(apps, schema_editor):
    """
    Drop the api_lote table and all its constraints and indexes.
    This table is obsolete since the Lote model was moved to fincas_app.
    """
    with schema_editor.connection.cursor() as cursor:
        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'api_lote'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            print("Table api_lote does not exist, skipping deletion")
            return
        
        # Drop constraints first
        constraints_to_drop = [
            'api_lote_area_positiva',
            'api_lote_fecha_cosecha_valida',
            'api_lote_identificador_unico_por_finca',
            'lote_area_positiva',
            'lote_fecha_cosecha_valida',
            'lote_identificador_unico_por_finca',
        ]
        
        for constraint_name in constraints_to_drop:
            cursor.execute(f"""
                ALTER TABLE api_lote 
                DROP CONSTRAINT IF EXISTS {constraint_name} CASCADE;
            """)
            print(f"Dropped constraint: {constraint_name}")
        
        # Drop indexes
        indexes_to_drop = [
            'api_lote_finca_created_idx',
            'api_lote_variedad_idx',
            'api_lote_estado_idx',
            'api_lote_activo_idx',
            'api_lote_finca_i_9482d1_idx',
            'api_lote_varieda_bd3734_idx',
            'api_lote_estado_4f08df_idx',
            'api_lote_activo_151304_idx',
        ]
        
        for index_name in indexes_to_drop:
            cursor.execute(f"""
                DROP INDEX IF EXISTS {index_name} CASCADE;
            """)
            print(f"Dropped index: {index_name}")
        
        # Drop foreign key constraints
        cursor.execute("""
            SELECT constraint_name
            FROM information_schema.table_constraints
            WHERE table_name = 'api_lote'
            AND constraint_type = 'FOREIGN KEY';
        """)
        fk_constraints = cursor.fetchall()
        
        for fk_constraint in fk_constraints:
            constraint_name = fk_constraint[0]
            cursor.execute(f"""
                ALTER TABLE api_lote 
                DROP CONSTRAINT IF EXISTS {constraint_name} CASCADE;
            """)
            print(f"Dropped foreign key: {constraint_name}")
        
        # Finally, drop the table
        cursor.execute("DROP TABLE IF EXISTS api_lote CASCADE;")
        print("Dropped table: api_lote")


def reverse_drop_api_lote_table(apps, schema_editor):
    """
    Reverse operation - this cannot be fully reversed as we don't have
    the exact structure. This is a one-way migration.
    """
    # This migration cannot be reversed safely
    # The table structure is not preserved
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_remove_duplicate_systemsettings'),
        ('fincas_app', '0013_normalize_lote_catalogos'),  # Ensure fincas_app has the normalized model
    ]

    operations = [
        migrations.RunPython(
            drop_api_lote_table,
            reverse_drop_api_lote_table,
        ),
    ]


