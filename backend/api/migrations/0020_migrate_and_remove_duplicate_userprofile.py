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
        
        # Drop all constraints first in the correct order:
        # 1. FOREIGN KEY constraints first (they reference other tables/primary keys)
        # 2. PRIMARY KEY constraint
        # 3. UNIQUE constraints
        # 4. CHECK constraints last (but skip NOT NULL checks on identity columns)
        cursor.execute("""
            SELECT constraint_name, constraint_type
            FROM information_schema.table_constraints
            WHERE table_schema = 'public'
            AND table_name = 'api_userprofile'
            AND constraint_type IN ('PRIMARY KEY', 'FOREIGN KEY', 'UNIQUE', 'CHECK')
            ORDER BY 
                CASE constraint_type
                    WHEN 'FOREIGN KEY' THEN 1
                    WHEN 'PRIMARY KEY' THEN 2
                    WHEN 'UNIQUE' THEN 3
                    WHEN 'CHECK' THEN 4
                END;
        """)
        constraints = cursor.fetchall()
        
        # Filter out CHECK constraints that are NOT NULL on identity columns (can't be dropped)
        # These are typically named like 'table_column_not_null'
        check_constraints_to_skip = set()
        for constraint in constraints:
            constraint_name = constraint[0]
            constraint_type = constraint[1]
            if constraint_type == 'CHECK' and '_not_null' in constraint_name.lower():
                # Check if this is a NOT NULL constraint on an identity column
                # We'll try to drop it, but if it fails, we'll skip it
                check_constraints_to_skip.add(constraint_name)
        
        for constraint in constraints:
            constraint_name = constraint[0]
            constraint_type = constraint[1]
            
            # Skip CHECK constraints that are likely NOT NULL on identity columns
            # These will be dropped when we drop the table
            if constraint_name in check_constraints_to_skip:
                print(f"Skipping {constraint_type.lower()}: {constraint_name} (NOT NULL on identity column)")
                continue
            
            # Use SAVEPOINT to handle errors without aborting the entire transaction
            # Sanitize savepoint name (only alphanumeric and underscore, max 63 chars)
            safe_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in constraint_name)
            savepoint_id = f"sp_{safe_name[:50]}_{abs(hash(constraint_name)) % 10000}"
            try:
                cursor.execute(f"SAVEPOINT {savepoint_id};")
                # Use quote_name to properly escape constraint names
                quoted_name = schema_editor.connection.ops.quote_name(constraint_name)
                cursor.execute(f"""
                    ALTER TABLE api_userprofile 
                    DROP CONSTRAINT IF EXISTS {quoted_name} CASCADE;
                """)
                cursor.execute(f"RELEASE SAVEPOINT {savepoint_id};")
                print(f"Dropped {constraint_type.lower()}: {constraint_name}")
            except Exception as e:
                # Rollback to savepoint to continue with other constraints
                try:
                    cursor.execute(f"ROLLBACK TO SAVEPOINT {savepoint_id};")
                except Exception as rollback_error:
                    # If rollback fails, the transaction is in a bad state
                    # We'll let Django handle it, but log the error
                    print(f"Error: Transaction state corrupted after failed constraint drop: {rollback_error}")
                    raise
                print(f"Warning: Could not drop constraint {constraint_name} ({constraint_type}): {e}")
                # Continue with other constraints
        
        # Drop remaining indexes (those not associated with constraints)
        # Note: PRIMARY KEY and UNIQUE constraints automatically create indexes,
        # so we need to drop indexes that are not part of constraints
        cursor.execute("""
            SELECT i.indexname
            FROM pg_indexes i
            WHERE i.schemaname = 'public'
            AND i.tablename = 'api_userprofile'
            AND NOT EXISTS (
                SELECT 1
                FROM pg_constraint c
                WHERE c.conname = i.indexname
            );
        """)
        indexes = cursor.fetchall()
        
        for index in indexes:
            index_name = index[0]
            # Use SAVEPOINT to handle errors without aborting the entire transaction
            # Sanitize savepoint name (only alphanumeric and underscore, max 63 chars)
            safe_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in index_name)
            savepoint_id = f"sp_idx_{safe_name[:50]}_{abs(hash(index_name)) % 10000}"
            try:
                cursor.execute(f"SAVEPOINT {savepoint_id};")
                # Use quote_name to properly escape index names
                quoted_name = schema_editor.connection.ops.quote_name(index_name)
                cursor.execute(f"""
                    DROP INDEX IF EXISTS {quoted_name} CASCADE;
                """)
                cursor.execute(f"RELEASE SAVEPOINT {savepoint_id};")
                print(f"Dropped index: {index_name}")
            except Exception as e:
                # Rollback to savepoint to continue with other indexes
                try:
                    cursor.execute(f"ROLLBACK TO SAVEPOINT {savepoint_id};")
                except Exception as rollback_error:
                    # If rollback fails, the transaction is in a bad state
                    # We'll let Django handle it, but log the error
                    print(f"Error: Transaction state corrupted after failed index drop: {rollback_error}")
                    raise
                print(f"Warning: Could not drop index {index_name}: {e}")
                # Continue with other indexes
        
        # Finally, drop the table
        try:
            cursor.execute("DROP TABLE IF EXISTS api_userprofile CASCADE;")
            print("Dropped table: api_userprofile")
        except Exception as e:
            print(f"Warning: Could not drop table api_userprofile: {e}")
            raise


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

