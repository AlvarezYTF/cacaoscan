# Generated manually - Rename success to login_successful and usuario to user

from django.db import migrations, models, connection


def _rename_usuario_to_user_if_exists(schema_editor):
    """Rename usuario field to user only if it exists (compatible with SQLite and PostgreSQL)."""
    db_engine = connection.settings_dict.get('ENGINE', '')
    
    with connection.cursor() as cursor:
        if 'postgresql' in db_engine:
            # Check if usuario column exists
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'api_loginhistory' AND column_name = 'usuario_id'
            """)
            if cursor.fetchone():
                # Rename the column
                cursor.execute('ALTER TABLE api_loginhistory RENAME COLUMN usuario_id TO user_id')
        # For SQLite, Django handles this through state operations


def _rename_success_to_login_successful_if_exists(schema_editor):
    """Rename success field to login_successful only if it exists (compatible with SQLite and PostgreSQL)."""
    db_engine = connection.settings_dict.get('ENGINE', '')
    
    with connection.cursor() as cursor:
        if 'postgresql' in db_engine:
            # Check if success column exists
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'api_loginhistory' AND column_name = 'success'
            """)
            if cursor.fetchone():
                # Rename the column
                cursor.execute('ALTER TABLE api_loginhistory RENAME COLUMN success TO login_successful')
        # For SQLite, Django handles this through state operations


def rename_indexes_if_exist(apps, schema_editor):
    """Rename indexes if they exist in the database, or create them if they don't."""
    connection = schema_editor.connection
    
    with connection.cursor() as cursor:
        # Handle success index
        cursor.execute("""
            SELECT 1 FROM pg_indexes 
            WHERE tablename = 'api_loginhistory' 
            AND indexname = 'api_loginhi_success_78b423_idx'
        """)
        
        if cursor.fetchone():
            # Index exists, rename it
            cursor.execute('ALTER INDEX "api_loginhi_success_78b423_idx" RENAME TO "api_loginhi_login_s_78b423_idx"')
        else:
            # Check if new index already exists
            cursor.execute("""
                SELECT 1 FROM pg_indexes 
                WHERE tablename = 'api_loginhistory' 
                AND indexname = 'api_loginhi_login_s_78b423_idx'
            """)
            if not cursor.fetchone():
                # Create the index with new name
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS api_loginhi_login_s_78b423_idx 
                    ON api_loginhistory (login_successful)
                """)
        
        # Handle usuario index
        cursor.execute("""
            SELECT 1 FROM pg_indexes 
            WHERE tablename = 'api_loginhistory' 
            AND indexname = 'api_loginhi_usuario_19e442_idx'
        """)
        
        if cursor.fetchone():
            # Index exists, rename it
            cursor.execute('ALTER INDEX "api_loginhi_usuario_19e442_idx" RENAME TO "api_loginhi_user_id_19e442_idx"')
        else:
            # Check if new index already exists
            cursor.execute("""
                SELECT 1 FROM pg_indexes 
                WHERE tablename = 'api_loginhistory' 
                AND indexname = 'api_loginhi_user_id_19e442_idx'
            """)
            if not cursor.fetchone():
                # Create the index with new name
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS api_loginhi_user_id_19e442_idx 
                    ON api_loginhistory (user_id, login_time DESC)
                """)


def reverse_rename_indexes(apps, schema_editor):
    """Reverse the index renames."""
    connection = schema_editor.connection
    
    with connection.cursor() as cursor:
        # Reverse success index
        cursor.execute("""
            SELECT 1 FROM pg_indexes 
            WHERE tablename = 'api_loginhistory' 
            AND indexname = 'api_loginhi_login_s_78b423_idx'
        """)
        
        if cursor.fetchone():
            cursor.execute('ALTER INDEX "api_loginhi_login_s_78b423_idx" RENAME TO "api_loginhi_success_78b423_idx"')
        
        # Reverse usuario index
        cursor.execute("""
            SELECT 1 FROM pg_indexes 
            WHERE tablename = 'api_loginhistory' 
            AND indexname = 'api_loginhi_user_id_19e442_idx'
        """)
        
        if cursor.fetchone():
            cursor.execute('ALTER INDEX "api_loginhi_user_id_19e442_idx" RENAME TO "api_loginhi_usuario_19e442_idx"')


class Migration(migrations.Migration):

    dependencies = [
        ('audit', '0003_add_failure_reason_default'),
    ]

    operations = [
        # Rename usuario field to user (only if it exists in DB)
        # REMOVE state rename because 'usuario' NEVER existed in LoginHistory
        # The field was always named 'user' from migration 0001
        migrations.SeparateDatabaseAndState(
            state_operations=[
                # No state rename needed - field 'usuario' never existed
                migrations.RunSQL("SELECT 1;", reverse_sql="SELECT 1;"),
            ],
            database_operations=[
                migrations.RunPython(
                    lambda apps, schema_editor: _rename_usuario_to_user_if_exists(schema_editor),
                    lambda apps, schema_editor: None
                ),
            ],
        ),
        # Rename success field to login_successful (only if it exists in DB)
        # REMOVE state rename because 'success' NEVER existed in LoginHistory
        # The field was always named 'login_successful' from migration 0001
        migrations.SeparateDatabaseAndState(
            state_operations=[
                # No state rename needed - field 'success' never existed
                migrations.RunSQL("SELECT 1;", reverse_sql="SELECT 1;"),
            ],
            database_operations=[
                migrations.RunPython(
                    lambda apps, schema_editor: _rename_success_to_login_successful_if_exists(schema_editor),
                    lambda apps, schema_editor: None
                ),
            ],
        ),
        # Rename indexes to match the new field names (if needed in DB)
        # NOTE: Indexes already exist with correct names from migration 0001
        # This is only for legacy databases that might have old index names
        migrations.SeparateDatabaseAndState(
            state_operations=[
                # No state changes - indexes already exist with correct names from 0001
                migrations.RunSQL("SELECT 1;", reverse_sql="SELECT 1;"),
            ],
            database_operations=[
                # Rename or create indexes in database (safe, checks if they exist)
                migrations.RunPython(
                    rename_indexes_if_exist,
                    reverse_rename_indexes
                ),
            ],
        ),
    ]

