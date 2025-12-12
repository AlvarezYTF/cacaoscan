# Fix indexes - handle missing indexes gracefully and update Django state
# -*- coding: utf-8 -*-
from django.db import migrations, connection


def fix_indexes(apps, schema_editor):
    """Fix indexes - skip if they don't exist."""
    db_alias = schema_editor.connection.alias
    with connection.cursor() as cursor:
        # List of index renames to attempt
        index_renames = [
            ('finca', 'api_finca_estado_idx', 'api_finca_estado__63f86d_idx'),
            ('finca', 'api_finca_tipo_suelo_idx', 'api_finca_tipo_su_e9b000_idx'),
            ('finca', 'api_finca_clima_idx', 'api_finca_clima_i_f6ba0a_idx'),
            ('lote', 'fincas_app__varieda_b2a31e_idx', 'fincas_app__varieda_30ab60_idx'),
            ('lote', 'fincas_app__estado_769498_idx', 'fincas_app__estado__fc8f6a_idx'),
        ]
        
        for model_name, old_name, new_name in index_renames:
            try:
                # Check if old index exists
                cursor.execute("""
                    SELECT 1 FROM pg_indexes 
                    WHERE indexname = %s
                """, [old_name])
                if cursor.fetchone():
                    # Check if new index already exists
                    cursor.execute("""
                        SELECT 1 FROM pg_indexes 
                        WHERE indexname = %s
                    """, [new_name])
                    if not cursor.fetchone():
                        cursor.execute(f'ALTER INDEX {old_name} RENAME TO {new_name}')
                        print(f"Renamed index {old_name} to {new_name}")
                    else:
                        # New index exists, drop old one
                        cursor.execute(f'DROP INDEX IF EXISTS {old_name}')
                        print(f"Dropped old index {old_name} (new one already exists)")
                else:
                    print(f"Index {old_name} does not exist, skipping")
            except Exception as e:
                print(f"Error processing index {old_name}: {e}")


def reverse_fix_indexes(apps, schema_editor):
    """Reverse - do nothing."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('fincas_app', '0013_normalize_lote_catalogos'),
    ]

    operations = [
        migrations.RunPython(
            fix_indexes,
            reverse_fix_indexes,
        ),
        # Use SeparateDatabaseAndState to update Django's state without changing DB
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.RenameIndex(
                    model_name='finca',
                    new_name='api_finca_estado__63f86d_idx',
                    old_name='api_finca_estado_idx',
                ),
                migrations.RenameIndex(
                    model_name='finca',
                    new_name='api_finca_tipo_su_e9b000_idx',
                    old_name='api_finca_tipo_suelo_idx',
                ),
                migrations.RenameIndex(
                    model_name='finca',
                    new_name='api_finca_clima_i_f6ba0a_idx',
                    old_name='api_finca_clima_idx',
                ),
                migrations.RenameIndex(
                    model_name='lote',
                    new_name='fincas_app__varieda_30ab60_idx',
                    old_name='fincas_app__varieda_b2a31e_idx',
                ),
                migrations.RenameIndex(
                    model_name='lote',
                    new_name='fincas_app__estado__fc8f6a_idx',
                    old_name='fincas_app__estado_769498_idx',
                ),
            ],
        ),
    ]

