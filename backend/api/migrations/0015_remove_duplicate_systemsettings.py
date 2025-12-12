# Generated manually - Remove duplicate SystemSettings table from api app
# SystemSettings model is now only in core app (core_systemsettings table)
# This migration removes the duplicate api_systemsettings table
# -*- coding: utf-8 -*-

from django.db import migrations


def migrate_systemsettings_data(apps, schema_editor):
    """
    Migrate data from api_systemsettings to core_systemsettings if needed.
    Only if api_systemsettings exists and has data, and core_systemsettings is empty.
    """
    db_alias = schema_editor.connection.alias
    
    # Check if api_systemsettings table exists
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'api_systemsettings'
            );
        """)
        api_table_exists = cursor.fetchone()[0]
        
        if not api_table_exists:
            return
        
        # Check if core_systemsettings exists and has data
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'core_systemsettings'
            );
        """)
        core_table_exists = cursor.fetchone()[0]
        
        if not core_table_exists:
            return
        
        # Check if api_systemsettings has data
        cursor.execute("SELECT COUNT(*) FROM api_systemsettings;")
        api_count = cursor.fetchone()[0]
        
        if api_count == 0:
            return
        
        # Check if core_systemsettings is empty
        cursor.execute("SELECT COUNT(*) FROM core_systemsettings;")
        core_count = cursor.fetchone()[0]
        
        # If core is empty and api has data, migrate it
        if core_count == 0 and api_count > 0:
            cursor.execute("""
                INSERT INTO core_systemsettings (
                    id, nombre_sistema, email_contacto, lema, logo,
                    recaptcha_enabled, session_timeout, login_attempts,
                    two_factor_auth, active_model, last_training,
                    created_at, updated_at
                )
                SELECT 
                    id, nombre_sistema, email_contacto, lema, logo,
                    recaptcha_enabled, session_timeout, login_attempts,
                    two_factor_auth, active_model, last_training,
                    created_at, updated_at
                FROM api_systemsettings
                ORDER BY id
                LIMIT 1;
            """)


def reverse_migrate_systemsettings_data(apps, schema_editor):
    """
    Reverse migration: copy data back from core_systemsettings to api_systemsettings.
    This is only for rollback purposes.
    """
    db_alias = schema_editor.connection.alias
    
    with schema_editor.connection.cursor() as cursor:
        # Check if both tables exist
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'api_systemsettings'
            );
        """)
        api_table_exists = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'core_systemsettings'
            );
        """)
        core_table_exists = cursor.fetchone()[0]
        
        if not api_table_exists or not core_table_exists:
            return
        
        # Recreate api_systemsettings table structure if it doesn't exist
        # (This would only happen if we're rolling back after dropping it)
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.columns 
            WHERE table_name = 'api_systemsettings';
        """)
        column_count = cursor.fetchone()[0]
        
        if column_count == 0:
            # Table was dropped, recreate it (for rollback)
            cursor.execute("""
                CREATE TABLE api_systemsettings (
                    id BIGSERIAL PRIMARY KEY,
                    nombre_sistema VARCHAR(100) DEFAULT 'CacaoScan',
                    email_contacto VARCHAR(254) DEFAULT 'contacto@cacaoscan.com',
                    lema VARCHAR(200) DEFAULT 'La mejor plataforma para el control de calidad del cacao',
                    logo VARCHAR(100),
                    recaptcha_enabled BOOLEAN DEFAULT TRUE,
                    session_timeout INTEGER DEFAULT 60,
                    login_attempts INTEGER DEFAULT 5,
                    two_factor_auth BOOLEAN DEFAULT FALSE,
                    active_model VARCHAR(50) DEFAULT 'yolov8',
                    last_training TIMESTAMP,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL
                );
            """)
        
        # Copy data from core to api
        cursor.execute("SELECT COUNT(*) FROM api_systemsettings;")
        api_count = cursor.fetchone()[0]
        
        if api_count == 0:
            cursor.execute("""
                INSERT INTO api_systemsettings (
                    id, nombre_sistema, email_contacto, lema, logo,
                    recaptcha_enabled, session_timeout, login_attempts,
                    two_factor_auth, active_model, last_training,
                    created_at, updated_at
                )
                SELECT 
                    id, nombre_sistema, email_contacto, lema, logo,
                    recaptcha_enabled, session_timeout, login_attempts,
                    two_factor_auth, active_model, last_training,
                    created_at, updated_at
                FROM core_systemsettings
                ORDER BY id
                LIMIT 1;
            """)


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_remove_activitylog_usuario_remove_cacaoimage_lote_and_more'),
        ('core', '0001_initial'),  # Ensure core SystemSettings exists
    ]

    operations = [
        # First, migrate any data from api_systemsettings to core_systemsettings
        migrations.RunPython(
            migrate_systemsettings_data,
            reverse_migrate_systemsettings_data,
        ),
        # Then, drop the duplicate table
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS api_systemsettings CASCADE;",
            reverse_sql="""
                CREATE TABLE IF NOT EXISTS api_systemsettings (
                    id BIGSERIAL PRIMARY KEY,
                    nombre_sistema VARCHAR(100) DEFAULT 'CacaoScan',
                    email_contacto VARCHAR(254) DEFAULT 'contacto@cacaoscan.com',
                    lema VARCHAR(200) DEFAULT 'La mejor plataforma para el control de calidad del cacao',
                    logo VARCHAR(100),
                    recaptcha_enabled BOOLEAN DEFAULT TRUE,
                    session_timeout INTEGER DEFAULT 60,
                    login_attempts INTEGER DEFAULT 5,
                    two_factor_auth BOOLEAN DEFAULT FALSE,
                    active_model VARCHAR(50) DEFAULT 'yolov8',
                    last_training TIMESTAMP,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL
                );
            """,
        ),
    ]

