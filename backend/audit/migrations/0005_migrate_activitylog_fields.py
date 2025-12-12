# Generated manually - Migrate ActivityLog fields from old schema to new schema
# Maps: accion -> action, usuario -> user, modelo -> resource_type, objeto_id -> resource_id

from django.db import migrations


def migrate_activitylog_fields(apps, schema_editor):
    """
    Migrate data from old field names to new field names.
    This handles the case where the table already exists with old field names.
    """
    connection = schema_editor.connection
    
    with connection.cursor() as cursor:
        # Check if old fields exist and new fields don't
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'api_activitylog'
        """)
        
        existing_columns = {row[0] for row in cursor.fetchall()}
        
        # If old fields exist, we need to migrate
        # Handle action field: rename accion to action, or add action if accion doesn't exist
        if 'accion' in existing_columns and 'action' not in existing_columns:
            # Rename accion to action
            cursor.execute('ALTER TABLE api_activitylog RENAME COLUMN accion TO action')
        elif 'action' not in existing_columns:
            # Add action field with a default value for existing rows
            cursor.execute("ALTER TABLE api_activitylog ADD COLUMN action VARCHAR(100) DEFAULT 'unknown' NOT NULL")
            cursor.execute("ALTER TABLE api_activitylog ALTER COLUMN action DROP DEFAULT")
        
        # Handle user field: rename usuario_id to user_id, or add user_id if usuario_id doesn't exist
        if 'usuario_id' in existing_columns and 'user_id' not in existing_columns:
            # Rename usuario_id to user_id (ForeignKey column)
            cursor.execute('ALTER TABLE api_activitylog RENAME COLUMN usuario_id TO user_id')
        elif 'user_id' not in existing_columns:
            # This shouldn't happen if the table was created correctly, but handle it anyway
            # We can't add a ForeignKey without a default, so this is a problem
            # For now, we'll assume the table structure is correct
            pass
        
        # Add new fields if they don't exist
        if 'resource_type' not in existing_columns:
            # Map from modelo if it exists, otherwise add as empty string
            if 'modelo' in existing_columns:
                cursor.execute('ALTER TABLE api_activitylog ADD COLUMN resource_type VARCHAR(50) DEFAULT \'\'')
                cursor.execute('UPDATE api_activitylog SET resource_type = modelo WHERE resource_type IS NULL')
                cursor.execute('ALTER TABLE api_activitylog ALTER COLUMN resource_type SET DEFAULT \'\'')
            else:
                cursor.execute('ALTER TABLE api_activitylog ADD COLUMN resource_type VARCHAR(50) DEFAULT \'\' NOT NULL')
        
        if 'resource_id' not in existing_columns:
            # Map from objeto_id if it exists, otherwise add as nullable integer
            if 'objeto_id' in existing_columns:
                cursor.execute('ALTER TABLE api_activitylog ADD COLUMN resource_id INTEGER')
                # Try to convert objeto_id (string) to integer, set NULL if conversion fails
                cursor.execute("""
                    UPDATE api_activitylog 
                    SET resource_id = CASE 
                        WHEN objeto_id ~ '^[0-9]+$' THEN objeto_id::INTEGER 
                        ELSE NULL 
                    END
                """)
            else:
                cursor.execute('ALTER TABLE api_activitylog ADD COLUMN resource_id INTEGER NULL')
        
        if 'details' not in existing_columns:
            # Combine datos_antes and datos_despues into details JSON
            cursor.execute('ALTER TABLE api_activitylog ADD COLUMN details JSONB DEFAULT \'{}\'')
            if 'datos_antes' in existing_columns and 'datos_despues' in existing_columns:
                cursor.execute("""
                    UPDATE api_activitylog 
                    SET details = jsonb_build_object(
                        'before', COALESCE(datos_antes, '{}'::jsonb),
                        'after', COALESCE(datos_despues, '{}'::jsonb)
                    )
                """)
            elif 'datos_antes' in existing_columns:
                cursor.execute("""
                    UPDATE api_activitylog 
                    SET details = jsonb_build_object('before', COALESCE(datos_antes, '{}'::jsonb))
                """)
            elif 'datos_despues' in existing_columns:
                cursor.execute("""
                    UPDATE api_activitylog 
                    SET details = jsonb_build_object('after', COALESCE(datos_despues, '{}'::jsonb))
                """)
        
        # Ensure user_agent has default empty string if it's nullable
        if 'user_agent' in existing_columns:
            cursor.execute("""
                SELECT is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'api_activitylog' AND column_name = 'user_agent'
            """)
            is_nullable = cursor.fetchone()[0] == 'YES'
            if is_nullable:
                cursor.execute("UPDATE api_activitylog SET user_agent = '' WHERE user_agent IS NULL")
                cursor.execute('ALTER TABLE api_activitylog ALTER COLUMN user_agent SET DEFAULT \'\'')
                cursor.execute('ALTER TABLE api_activitylog ALTER COLUMN user_agent SET NOT NULL')


def reverse_migrate_activitylog_fields(apps, schema_editor):
    """Reverse migration - not typically needed, but included for completeness."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('audit', '0004_rename_success_to_login_successful'),
    ]

    operations = [
        migrations.RunPython(
            migrate_activitylog_fields,
            reverse_migrate_activitylog_fields
        ),
    ]

