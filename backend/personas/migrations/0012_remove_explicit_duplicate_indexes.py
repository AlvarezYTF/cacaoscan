# Generated manually - Remove explicit duplicate indexes from Persona model
# Django automatically creates indexes for ForeignKeys and unique fields
# This migration removes the explicit indexes defined in the model Meta.indexes
# -*- coding: utf-8 -*-

from django.db import migrations


def remove_explicit_indexes(apps, schema_editor):
    """
    Remove explicit indexes from personas_persona that are duplicates of Django's auto-created indexes.
    Django automatically creates:
    - Unique indexes for unique=True fields (numero_documento, telefono)
    - Indexes for ForeignKeys and OneToOneField (user, tipo_documento, genero, municipio)
    """
    with schema_editor.connection.cursor() as cursor:
        # List of explicit indexes to remove (these are duplicates)
        explicit_indexes_to_remove = [
            'personas_pe_numero__8c4625_idx',  # Explicit index on numero_documento (Django creates unique index)
            'personas_pe_telefon_c9eac3_idx',  # Explicit index on telefono (Django creates unique index)
            'personas_pe_user_id_0b4abb_idx',  # Explicit index on user (Django creates index for OneToOneField)
        ]
        
        for idx_name in explicit_indexes_to_remove:
            try:
                cursor.execute(f'DROP INDEX IF EXISTS {idx_name} CASCADE;')
                print(f"Dropped explicit duplicate index: {idx_name}")
            except Exception as e:
                print(f"Error dropping index {idx_name}: {e}")


def reverse_remove_explicit_indexes(apps, schema_editor):
    """
    Reverse migration - cannot safely recreate dropped indexes.
    """
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('personas', '0013_merge_0011_remove_indexes'),
    ]

    operations = [
        migrations.RunPython(
            remove_explicit_indexes,
            reverse_remove_explicit_indexes,
        ),
        # Remove indexes from model Meta (using RunSQL to handle gracefully if they don't exist)
        migrations.RunSQL(
            sql="""
                DROP INDEX IF EXISTS personas_pe_numero__8c4625_idx CASCADE;
                DROP INDEX IF EXISTS personas_pe_telefon_c9eac3_idx CASCADE;
                DROP INDEX IF EXISTS personas_pe_user_id_0b4abb_idx CASCADE;
            """,
            reverse_sql="""
                -- Cannot safely recreate indexes in reverse
                SELECT 1;
            """,
        ),
    ]

