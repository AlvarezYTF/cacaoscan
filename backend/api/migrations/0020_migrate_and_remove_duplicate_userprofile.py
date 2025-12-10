# Generated manually - Migrate data from api_userprofile to auth_app_userprofile and remove duplicate
# This table was created in migration 0002 but the model was moved to auth_app
# The table api_userprofile is now obsolete and should be removed
# All data should be migrated to auth_app_userprofile
# -*- coding: utf-8 -*-

from django.db import migrations


def migrate_userprofile_data(apps, schema_editor):
    """
    Migrate data from api_userprofile to auth_app_userprofile if needed.
    Maps fields and handles differences in structure.
    """
    with schema_editor.connection.cursor() as cursor:
        # Check if api_userprofile table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'api_userprofile'
            );
        """)
        api_table_exists = cursor.fetchone()[0]
        
        if not api_table_exists:
            print("Table api_userprofile does not exist, skipping migration")
            return
        
        # Check if auth_app_userprofile exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'auth_app_userprofile'
            );
        """)
        auth_table_exists = cursor.fetchone()[0]
        
        if not auth_table_exists:
            print("Table auth_app_userprofile does not exist, skipping migration")
            return
        
        # Check if api_userprofile has data
        cursor.execute("SELECT COUNT(*) FROM api_userprofile;")
        api_count = cursor.fetchone()[0]
        
        if api_count == 0:
            print("Table api_userprofile is empty, no data to migrate")
            return
        
        # Check which users already have profiles in auth_app
        cursor.execute("""
            SELECT user_id FROM auth_app_userprofile;
        """)
        existing_user_ids = {row[0] for row in cursor.fetchall()}
        
        # Get all records from api_userprofile that don't exist in auth_app
        cursor.execute("""
            SELECT 
                user_id, years_experience, farm_size_hectares, 
                preferred_language, email_notifications,
                created_at, updated_at, municipality, region
            FROM api_userprofile
            WHERE user_id NOT IN (SELECT user_id FROM auth_app_userprofile WHERE user_id IS NOT NULL)
            ORDER BY user_id;
        """)
        api_profiles = cursor.fetchall()
        
        if not api_profiles:
            print("All users from api_userprofile already have profiles in auth_app_userprofile")
            return
        
        print(f"Migrating {len(api_profiles)} records from api_userprofile to auth_app_userprofile")
        
        migrated = 0
        skipped = 0
        
        for profile in api_profiles:
            (user_id, years_experience, farm_size_hectares, 
             preferred_language, email_notifications,
             created_at, updated_at, municipality, region) = profile
            
            # Try to find municipio by name
            municipio_id = None
            if municipality:
                # Try to find municipio by name (case insensitive)
                cursor.execute("""
                    SELECT id FROM catalogos_municipio 
                    WHERE LOWER(nombre) = LOWER(%s)
                    LIMIT 1;
                """, [municipality])
                result = cursor.fetchone()
                if result:
                    municipio_id = result[0]
            
            # If not found by municipality, try by region (departamento)
            if not municipio_id and region:
                cursor.execute("""
                    SELECT m.id 
                    FROM catalogos_municipio m
                    JOIN catalogos_departamento d ON m.departamento_id = d.id
                    WHERE LOWER(d.nombre) = LOWER(%s)
                    LIMIT 1;
                """, [region])
                result = cursor.fetchone()
                if result:
                    municipio_id = result[0]
            
            # Insert into auth_app_userprofile
            # Note: farm_name is NOT migrated - it belongs to Finca, not UserProfile (3NF compliance)
            # Note: region and municipality are converted to municipio_id (normalized FK)
            try:
                cursor.execute("""
                    INSERT INTO auth_app_userprofile (
                        user_id, municipio_id, years_experience, farm_size_hectares,
                        preferred_language, email_notifications, created_at, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (user_id) DO NOTHING;
                """, [
                    user_id, municipio_id, years_experience, farm_size_hectares,
                    preferred_language, email_notifications, created_at, updated_at
                ])
                migrated += 1
            except Exception as e:
                print(f"Warning: Could not migrate profile for user_id {user_id}: {e}")
                skipped += 1
        
        if municipality or region:
            print(f"Note: {len([p for p in api_profiles if p[7] or p[8]])} profiles had municipality/region data")
            print("These were converted to municipio_id (normalized FK) or set to NULL if no match found")
        
        print(f"Migrated {migrated} profiles, skipped {skipped}")


def reverse_migrate_userprofile_data(apps, schema_editor):
    """
    Reverse migration: copy data back from auth_app_userprofile to api_userprofile.
    This is only for rollback purposes.
    """
    with schema_editor.connection.cursor() as cursor:
        # Check if both tables exist
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'api_userprofile'
            );
        """)
        api_table_exists = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'auth_app_userprofile'
            );
        """)
        auth_table_exists = cursor.fetchone()[0]
        
        if not api_table_exists or not auth_table_exists:
            return
        
        # Copy data from auth to api (only common fields)
        cursor.execute("""
            INSERT INTO api_userprofile (
                user_id, years_experience, farm_size_hectares,
                preferred_language, email_notifications, created_at, updated_at
            )
            SELECT 
                user_id, years_experience, farm_size_hectares,
                preferred_language, email_notifications, created_at, updated_at
            FROM auth_app_userprofile
            WHERE user_id NOT IN (SELECT user_id FROM api_userprofile WHERE user_id IS NOT NULL)
            ON CONFLICT (user_id) DO NOTHING;
        """)


def drop_api_userprofile_table(apps, schema_editor):
    """
    Drop the api_userprofile table and all its constraints and indexes.
    This table is obsolete since the UserProfile model was moved to auth_app.
    """
    with schema_editor.connection.cursor() as cursor:
        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'api_userprofile'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            print("Table api_userprofile does not exist, skipping deletion")
            return
        
        # Drop all constraints first (PRIMARY KEY, FOREIGN KEY, UNIQUE, CHECK)
        # This must be done before dropping indexes, as PRIMARY KEY constraints create indexes
        cursor.execute("""
            SELECT constraint_name, constraint_type
            FROM information_schema.table_constraints
            WHERE table_name = 'api_userprofile'
            AND constraint_type IN ('PRIMARY KEY', 'FOREIGN KEY', 'UNIQUE', 'CHECK');
        """)
        constraints = cursor.fetchall()
        
        for constraint in constraints:
            constraint_name = constraint[0]
            constraint_type = constraint[1]
            # Use format with %I to properly escape constraint names (handles names starting with numbers, special chars, etc.)
            # %I in format() automatically quotes identifiers
            cursor.execute(f"""
                ALTER TABLE api_userprofile 
                DROP CONSTRAINT IF EXISTS {schema_editor.connection.ops.quote_name(constraint_name)} CASCADE;
            """)
            print(f"Dropped {constraint_type.lower()}: {constraint_name}")
        
        # Drop remaining indexes (those not associated with constraints)
        # Note: PRIMARY KEY and UNIQUE constraints automatically create indexes,
        # so we need to drop indexes that are not part of constraints
        cursor.execute("""
            SELECT i.indexname
            FROM pg_indexes i
            WHERE i.tablename = 'api_userprofile'
            AND NOT EXISTS (
                SELECT 1
                FROM pg_constraint c
                WHERE c.conname = i.indexname
            );
        """)
        indexes = cursor.fetchall()
        
        for index in indexes:
            index_name = index[0]
            # Use quote_name to properly escape index names (handles names starting with numbers, special chars, etc.)
            cursor.execute(f"""
                DROP INDEX IF EXISTS {schema_editor.connection.ops.quote_name(index_name)} CASCADE;
            """)
            print(f"Dropped index: {index_name}")
        
        # Finally, drop the table
        cursor.execute("DROP TABLE IF EXISTS api_userprofile CASCADE;")
        print("Dropped table: api_userprofile")


def reverse_drop_api_userprofile_table(apps, schema_editor):
    """
    Reverse operation - this cannot be fully reversed as we don't have
    the exact structure. This is a one-way migration.
    """
    # This migration cannot be reversed safely
    # The table structure is not preserved
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0019_merge_0016_remove_tables'),
        ('auth_app', '0005_remove_userprofile_phone_number'),  # Ensure auth_app UserProfile exists and is normalized
    ]

    operations = [
        # First, migrate any data from api_userprofile to auth_app_userprofile
        migrations.RunPython(
            migrate_userprofile_data,
            reverse_migrate_userprofile_data,
        ),
        # Then, drop the duplicate table
        migrations.RunPython(
            drop_api_userprofile_table,
            reverse_drop_api_userprofile_table,
        ),
    ]

