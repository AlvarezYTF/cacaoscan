# Generated manually - Remove duplicate indexes from personas_persona
# Django automatically creates indexes for ForeignKeys and unique fields
# This migration removes explicit duplicate indexes, keeping Django's auto-created ones
# -*- coding: utf-8 -*-

from django.db import migrations


def remove_duplicate_indexes(apps, schema_editor):
    """
    Remove duplicate indexes from personas_persona.
    Django automatically creates:
    - Indexes for ForeignKeys (pattern: tablename_field_id_xxxxx_idx)
    - Unique indexes for unique=True fields (pattern: tablename_field_xxxxx_uniq)
    - Indexes for OneToOneField (pattern: tablename_field_id_xxxxx_idx)
    
    So we remove explicit duplicate indexes and keep Django's auto-created ones.
    """
    with schema_editor.connection.cursor() as cursor:
        # Get all indexes for personas_persona table
        cursor.execute("""
            SELECT 
                indexname,
                indexdef
            FROM pg_indexes 
            WHERE tablename = 'personas_persona'
            ORDER BY indexname;
        """)
        
        all_indexes = cursor.fetchall()
        
        # Map column names to their indexes
        column_indexes = {
            'user_id': [],
            'numero_documento': [],
            'telefono': [],
            'tipo_documento_id': [],
            'genero_id': [],
            'municipio_id': [],
        }
        
        # Categorize indexes by column
        for idx_name, idx_def in all_indexes:
            idx_def_lower = idx_def.lower()
            
            if 'user_id' in idx_def_lower or ('user' in idx_name.lower() and 'user_id' in idx_def_lower):
                column_indexes['user_id'].append((idx_name, idx_def))
            elif 'numero_documento' in idx_def_lower or 'numero_documento' in idx_name.lower():
                column_indexes['numero_documento'].append((idx_name, idx_def))
            elif 'telefono' in idx_def_lower or 'telefono' in idx_name.lower():
                column_indexes['telefono'].append((idx_name, idx_def))
            elif 'tipo_documento_id' in idx_def_lower:
                column_indexes['tipo_documento_id'].append((idx_name, idx_def))
            elif 'genero_id' in idx_def_lower:
                column_indexes['genero_id'].append((idx_name, idx_def))
            elif 'municipio_id' in idx_def_lower:
                column_indexes['municipio_id'].append((idx_name, idx_def))
        
        # Identify and drop duplicate indexes
        indexes_to_drop = []
        
        for column, indexes in column_indexes.items():
            if len(indexes) > 1:
                # Identify auto index vs explicit
                auto_indexes = []
                explicit_indexes = []
                
                for idx_name, idx_def in indexes:
                    # Django auto index patterns:
                    # - For FKs: personas_persona_field_id_xxxxx_idx
                    # - For unique: personas_persona_field_xxxxx_uniq
                    # - For explicit: custom names like personas_pe_numero__8c4625_idx
                    
                    is_auto = False
                    
                    # Check if it's a unique constraint index (Django pattern)
                    if '_uniq' in idx_name or 'unique' in idx_def_lower:
                        is_auto = True
                    # Check if it's a FK auto index (pattern: _field_id_xxxxx_idx)
                    elif f'_{column}_' in idx_name and idx_name.endswith('_idx') and len(idx_name.split('_')) >= 5:
                        is_auto = True
                    # Check if it's a simple FK index (pattern: field_id_xxxxx)
                    elif column.endswith('_id') and f'{column}_' in idx_name:
                        is_auto = True
                    
                    if is_auto:
                        auto_indexes.append((idx_name, idx_def))
                    else:
                        explicit_indexes.append((idx_name, idx_def))
                
                # For unique fields (numero_documento, telefono), Django creates unique indexes
                # We should keep the unique index and drop explicit non-unique indexes
                if column in ['numero_documento', 'telefono']:
                    unique_indexes = [idx for idx in all_indexes if 'unique' in idx[1].lower() or '_uniq' in idx[0]]
                    if unique_indexes:
                        # Keep unique index, drop explicit non-unique
                        for idx_name, _ in explicit_indexes:
                            if idx_name not in [u[0] for u in unique_indexes]:
                                indexes_to_drop.append(idx_name)
                    else:
                        # Keep auto, drop explicit
                        for idx_name, _ in explicit_indexes:
                            indexes_to_drop.append(idx_name)
                else:
                    # For FKs, keep auto index, drop explicit
                    for idx_name, _ in explicit_indexes:
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
        ('personas', '0010_alter_persona_municipio'),
    ]

    operations = [
        migrations.RunPython(
            remove_duplicate_indexes,
            reverse_remove_duplicate_indexes,
        ),
    ]


