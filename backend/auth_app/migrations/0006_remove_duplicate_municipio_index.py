# Generated manually - Remove duplicate index on municipio_id
# Django automatically creates an index for ForeignKey fields, so the explicit
# index auth_app_us_municip_97842b_idx is redundant with the automatic one
# auth_app_userprofile_municipio_id_7ec589e8
# -*- coding: utf-8 -*-

from django.db import migrations


def remove_duplicate_index(apps, schema_editor):
    """
    Remove the duplicate index auth_app_us_municip_97842b_idx.
    Django automatically creates an index for ForeignKey fields, so this explicit
    index is redundant.
    """
    with schema_editor.connection.cursor() as cursor:
        # Check if the index exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM pg_indexes 
                WHERE tablename = 'auth_app_userprofile' 
                AND indexname = 'auth_app_us_municip_97842b_idx'
            );
        """)
        index_exists = cursor.fetchone()[0]
        
        if not index_exists:
            print("Index auth_app_us_municip_97842b_idx does not exist, skipping removal")
            return
        
        # Drop the duplicate index
        cursor.execute("DROP INDEX IF EXISTS auth_app_us_municip_97842b_idx CASCADE;")
        print("Removed duplicate index: auth_app_us_municip_97842b_idx")
        
        # Verify the automatic ForeignKey index still exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM pg_indexes 
                WHERE tablename = 'auth_app_userprofile' 
                AND indexname LIKE 'auth_app_userprofile_municipio_id%'
            );
        """)
        fk_index_exists = cursor.fetchone()[0]
        
        if fk_index_exists:
            print("Automatic ForeignKey index on municipio_id is still present")
        else:
            print("Warning: Automatic ForeignKey index on municipio_id not found")


def reverse_remove_duplicate_index(apps, schema_editor):
    """
    Reverse operation: recreate the explicit index.
    This is only for rollback purposes.
    """
    with schema_editor.connection.cursor() as cursor:
        # Check if the index already exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM pg_indexes 
                WHERE tablename = 'auth_app_userprofile' 
                AND indexname = 'auth_app_us_municip_97842b_idx'
            );
        """)
        index_exists = cursor.fetchone()[0]
        
        if index_exists:
            print("Index auth_app_us_municip_97842b_idx already exists, skipping recreation")
            return
        
        # Recreate the explicit index
        cursor.execute("""
            CREATE INDEX auth_app_us_municip_97842b_idx 
            ON auth_app_userprofile (municipio_id);
        """)
        print("Recreated index: auth_app_us_municip_97842b_idx")


class Migration(migrations.Migration):

    dependencies = [
        ('auth_app', '0005_remove_userprofile_phone_number'),
    ]

    operations = [
        migrations.RunPython(
            remove_duplicate_index,
            reverse_remove_duplicate_index,
        ),
    ]


