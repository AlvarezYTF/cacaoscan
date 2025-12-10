# Generated manually - Remove duplicate indexes from api_finca
# Django automatically creates indexes for ForeignKeys, so explicit indexes on FK columns are redundant
# This migration removes the explicit duplicate indexes, keeping Django's auto-created ones
# -*- coding: utf-8 -*-

from django.db import migrations


def remove_duplicate_indexes(apps, schema_editor):
    """
    Remove duplicate indexes from api_finca.
    Django automatically creates indexes for ForeignKeys (pattern: tablename_field_id_xxxxx_idx),
    so we remove the explicit duplicate indexes and keep Django's auto-created ones.
    """
    with schema_editor.connection.cursor() as cursor:
        # Get all indexes for api_finca table
        cursor.execute("""
            SELECT 
                indexname,
                indexdef
            FROM pg_indexes 
            WHERE tablename = 'api_finca'
            ORDER BY indexname;
        """)
        
        all_indexes = cursor.fetchall()
        
        # Map column names to their indexes
        column_indexes = {
            'clima_id': [],
            'estado_id': [],
            'municipio_id': [],
            'tipo_suelo_id': [],
            'agricultor_id': [],
        }
        
        # Categorize indexes by column
        for idx_name, idx_def in all_indexes:
            idx_def_lower = idx_def.lower()
            
            if 'clima_id' in idx_def_lower or 'clima' in idx_name.lower():
                column_indexes['clima_id'].append((idx_name, idx_def))
            elif 'estado_id' in idx_def_lower or ('estado' in idx_name.lower() and 'estado_id' in idx_def_lower):
                column_indexes['estado_id'].append((idx_name, idx_def))
            elif 'municipio_id' in idx_def_lower or ('municipio' in idx_name.lower() and 'municipio_id' in idx_def_lower):
                column_indexes['municipio_id'].append((idx_name, idx_def))
            elif 'tipo_suelo_id' in idx_def_lower or ('tipo_suelo' in idx_name.lower() and 'tipo_suelo_id' in idx_def_lower):
                column_indexes['tipo_suelo_id'].append((idx_name, idx_def))
            elif 'agricultor_id' in idx_def_lower or ('agricultor' in idx_name.lower() and 'agricultor_id' in idx_def_lower):
                column_indexes['agricultor_id'].append((idx_name, idx_def))
        
        # Identify and drop duplicate indexes
        indexes_to_drop = []
        
        for column, indexes in column_indexes.items():
            if len(indexes) > 1:
                # Identify auto index (Django pattern: ends with _id_xxxxx_idx) vs explicit
                auto_indexes = []
                explicit_indexes = []
                
                for idx_name, idx_def in indexes:
                    # Django auto index pattern: api_finca_field_id_xxxxx_idx
                    if f'_{column}_' in idx_name and idx_name.endswith('_idx') and len(idx_name.split('_')) >= 5:
                        auto_indexes.append((idx_name, idx_def))
                    else:
                        explicit_indexes.append((idx_name, idx_def))
                
                # Keep auto indexes, drop explicit duplicates
                # Exception: for agricultor_id, we have a composite index that we want to keep
                if column == 'agricultor_id':
                    # Check if there's a composite index (contains created_at)
                    composite_indexes = [idx for idx in explicit_indexes if 'created_at' in idx[1].lower()]
                    if composite_indexes:
                        # Keep composite, drop simple auto index
                        for idx_name, _ in auto_indexes:
                            if 'created_at' not in idx_name.lower():
                                indexes_to_drop.append(idx_name)
                    else:
                        # Keep auto, drop explicit
                        for idx_name, _ in explicit_indexes:
                            indexes_to_drop.append(idx_name)
                else:
                    # For other columns, keep auto index, drop explicit
                    for idx_name, _ in explicit_indexes:
                        indexes_to_drop.append(idx_name)
        
        # Also handle specific known duplicates mentioned by user
        known_duplicates = [
            'api_finca_clima_i_f6ba0a_idx',  # Explicit, drop this
            'api_finca_clima_id_24830cb9',   # Auto, keep this
        ]
        
        # Check which ones exist and drop the explicit one
        for idx_name in known_duplicates:
            cursor.execute("""
                SELECT indexname FROM pg_indexes 
                WHERE tablename = 'api_finca' AND indexname = %s
            """, [idx_name])
            if cursor.fetchone():
                # This is the explicit one (shorter name), drop it
                if idx_name == 'api_finca_clima_i_f6ba0a_idx' and idx_name not in indexes_to_drop:
                    indexes_to_drop.append(idx_name)
        
        # Drop duplicate indexes
        for idx_name in indexes_to_drop:
            try:
                cursor.execute(f'DROP INDEX IF EXISTS {idx_name} CASCADE;')
                print(f"Dropped duplicate index: {idx_name}")
            except Exception as e:
                print(f"Error dropping index {idx_name}: {e}")


def reverse_remove_duplicate_indexes(apps, schema_editor):
    """
    Reverse migration - cannot safely recreate dropped indexes.
    """
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('fincas_app', '0016_merge_0014_fix_indexes_and_verify'),
    ]

    operations = [
        migrations.RunPython(
            remove_duplicate_indexes,
            reverse_remove_duplicate_indexes,
        ),
    ]

