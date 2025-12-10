# Generated manually - Add check constraints to ActivityLog for data integrity
# -*- coding: utf-8 -*-

from django.db import migrations


def add_activitylog_check_constraints(apps, schema_editor):
    """
    Add check constraints to ActivityLog to ensure data integrity:
    - If resource_type is provided, it should be a valid model name
    - If resource_id is provided, resource_type should also be provided (for legacy fields)
    - Ensure content_type and object_id are used together (for ContentType fields)
    """
    with schema_editor.connection.cursor() as cursor:
        # Check constraint: If resource_id is not NULL, resource_type should not be empty
        # This ensures legacy fields are used correctly
        cursor.execute("""
            DO $$ 
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint 
                    WHERE conname = 'api_activitylog_resource_id_requires_type_check'
                ) THEN
                    ALTER TABLE api_activitylog 
                    ADD CONSTRAINT api_activitylog_resource_id_requires_type_check
                    CHECK (
                        (resource_id IS NULL) OR 
                        (resource_type IS NOT NULL AND resource_type != '')
                    );
                END IF;
            END $$;
        """)
        
        # Check constraint: If object_id is not NULL, content_type should not be NULL
        # This ensures ContentType fields are used correctly
        cursor.execute("""
            DO $$ 
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint 
                    WHERE conname = 'api_activitylog_object_id_requires_content_type_check'
                ) THEN
                    ALTER TABLE api_activitylog 
                    ADD CONSTRAINT api_activitylog_object_id_requires_content_type_check
                    CHECK (
                        (object_id IS NULL) OR 
                        (content_type_id IS NOT NULL)
                    );
                END IF;
            END $$;
        """)
        
        # Check constraint: resource_type should be a valid model name format
        # Valid format: alphanumeric, dots, underscores (e.g., "CacaoImage", "images_app.cacaoimage")
        cursor.execute("""
            DO $$ 
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint 
                    WHERE conname = 'api_activitylog_resource_type_format_check'
                ) THEN
                    ALTER TABLE api_activitylog 
                    ADD CONSTRAINT api_activitylog_resource_type_format_check
                    CHECK (
                        (resource_type = '') OR 
                        (resource_type ~ '^[a-zA-Z0-9_.]+$')
                    );
                END IF;
            END $$;
        """)
        
        print("✓ Added check constraints to ActivityLog")


def remove_activitylog_check_constraints(apps, schema_editor):
    """
    Remove check constraints from ActivityLog.
    """
    with schema_editor.connection.cursor() as cursor:
        constraints = [
            'api_activitylog_resource_id_requires_type_check',
            'api_activitylog_object_id_requires_content_type_check',
            'api_activitylog_resource_type_format_check',
        ]
        
        for constraint_name in constraints:
            cursor.execute(f"""
                DO $$ 
                BEGIN
                    IF EXISTS (
                        SELECT 1 FROM pg_constraint 
                        WHERE conname = '{constraint_name}'
                    ) THEN
                        ALTER TABLE api_activitylog DROP CONSTRAINT IF EXISTS {constraint_name};
                    END IF;
                END $$;
            """)
        
        print("✓ Removed check constraints from ActivityLog")


class Migration(migrations.Migration):

    dependencies = [
        ('audit', '0011_remove_duplicate_activitylog_index'),
    ]

    operations = [
        migrations.RunPython(
            add_activitylog_check_constraints,
            remove_activitylog_check_constraints,
        ),
    ]

