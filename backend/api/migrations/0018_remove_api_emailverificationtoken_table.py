# Generated manually - Remove api_emailverificationtoken table from database
# This table was created in migration 0001 but the model was moved to auth_app
# The table api_emailverificationtoken is now obsolete and should be removed
# All data should already be in auth_app_emailverificationtoken
# -*- coding: utf-8 -*-

from django.db import migrations


def migrate_emailverificationtoken_data(apps, schema_editor):
    """
    Migrate data from api_emailverificationtoken to auth_app_emailverificationtoken if needed.
    Only if api_emailverificationtoken exists and has data, and auth_app_emailverificationtoken is empty.
    """
    with schema_editor.connection.cursor() as cursor:
        # Check if api_emailverificationtoken table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'api_emailverificationtoken'
            );
        """)
        api_table_exists = cursor.fetchone()[0]
        
        if not api_table_exists:
            print("Table api_emailverificationtoken does not exist, skipping migration")
            return
        
        # Check if auth_app_emailverificationtoken exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'auth_app_emailverificationtoken'
            );
        """)
        auth_table_exists = cursor.fetchone()[0]
        
        if not auth_table_exists:
            print("Table auth_app_emailverificationtoken does not exist, skipping migration")
            return
        
        # Check if api_emailverificationtoken has data
        cursor.execute("SELECT COUNT(*) FROM api_emailverificationtoken;")
        api_count = cursor.fetchone()[0]
        
        if api_count == 0:
            print("Table api_emailverificationtoken is empty, no data to migrate")
            return
        
        # Check if auth_app_emailverificationtoken is empty
        cursor.execute("SELECT COUNT(*) FROM auth_app_emailverificationtoken;")
        auth_count = cursor.fetchone()[0]
        
        # If auth is empty and api has data, migrate it
        if auth_count == 0 and api_count > 0:
            print(f"Migrating {api_count} records from api_emailverificationtoken to auth_app_emailverificationtoken")
            cursor.execute("""
                INSERT INTO auth_app_emailverificationtoken (
                    id, user_id, token, created_at, verified_at, is_verified
                )
                SELECT 
                    id, user_id, token, created_at, verified_at, is_verified
                FROM api_emailverificationtoken
                ON CONFLICT (user_id) DO NOTHING;
            """)
            print(f"Migrated {api_count} records successfully")
        else:
            print(f"auth_app_emailverificationtoken already has {auth_count} records, skipping migration")


def reverse_migrate_emailverificationtoken_data(apps, schema_editor):
    """
    Reverse migration: copy data back from auth_app_emailverificationtoken to api_emailverificationtoken.
    This is only for rollback purposes.
    """
    with schema_editor.connection.cursor() as cursor:
        # Check if both tables exist
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'api_emailverificationtoken'
            );
        """)
        api_table_exists = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'auth_app_emailverificationtoken'
            );
        """)
        auth_table_exists = cursor.fetchone()[0]
        
        if not api_table_exists or not auth_table_exists:
            return
        
        # Recreate api_emailverificationtoken table structure if it doesn't exist
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.columns 
            WHERE table_name = 'api_emailverificationtoken';
        """)
        column_count = cursor.fetchone()[0]
        
        if column_count == 0:
            # Table was dropped, recreate it (for rollback)
            cursor.execute("""
                CREATE TABLE api_emailverificationtoken (
                    id BIGSERIAL PRIMARY KEY,
                    token UUID UNIQUE NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    verified_at TIMESTAMP,
                    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
                    user_id INTEGER NOT NULL UNIQUE,
                    CONSTRAINT api_emailverificationtoken_user_id_fkey 
                        FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE
                );
            """)
        
        # Copy data from auth to api
        cursor.execute("SELECT COUNT(*) FROM api_emailverificationtoken;")
        api_count = cursor.fetchone()[0]
        
        if api_count == 0:
            cursor.execute("""
                INSERT INTO api_emailverificationtoken (
                    id, user_id, token, created_at, verified_at, is_verified
                )
                SELECT 
                    id, user_id, token, created_at, verified_at, is_verified
                FROM auth_app_emailverificationtoken
                ON CONFLICT (user_id) DO NOTHING;
            """)


def drop_api_emailverificationtoken_table(apps, schema_editor):
    """
    Drop the api_emailverificationtoken table and all its constraints and indexes.
    This table is obsolete since the EmailVerificationToken model was moved to auth_app.
    Using CASCADE to automatically drop all constraints and indexes.
    """
    with schema_editor.connection.cursor() as cursor:
        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'api_emailverificationtoken'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            print("Table api_emailverificationtoken does not exist, skipping deletion")
            return
        
        # Drop the table directly with CASCADE
        # This will automatically drop all constraints (PRIMARY KEY, FOREIGN KEY, UNIQUE)
        # and all indexes associated with the table
        cursor.execute("DROP TABLE IF EXISTS api_emailverificationtoken CASCADE;")
        print("Dropped table: api_emailverificationtoken (with all constraints and indexes)")


def reverse_drop_api_emailverificationtoken_table(apps, schema_editor):
    """
    Reverse operation - this cannot be fully reversed as we don't have
    the exact structure. This is a one-way migration.
    """
    # This migration cannot be reversed safely
    # The table structure is not preserved
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0017_migrate_and_remove_duplicate_cacao_tables'),
        ('auth_app', '0001_initial'),  # Ensure auth_app EmailVerificationToken exists
    ]

    operations = [
        # First, migrate any data from api_emailverificationtoken to auth_app_emailverificationtoken
        migrations.RunPython(
            migrate_emailverificationtoken_data,
            reverse_migrate_emailverificationtoken_data,
        ),
        # Then, drop the duplicate table
        migrations.RunPython(
            drop_api_emailverificationtoken_table,
            reverse_drop_api_emailverificationtoken_table,
        ),
    ]

