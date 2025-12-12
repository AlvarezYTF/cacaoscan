# Generated manually - Migrate data from api_cacaoimage/api_cacaoprediction to images_app tables and remove duplicates
# -*- coding: utf-8 -*-

from django.db import migrations


def migrate_cacao_data_forward(apps, schema_editor):
    """
    Migrate data from api_cacaoimage/api_cacaoprediction to images_app tables if they exist.
    This handles the case where data exists in the old api tables.
    """
    db_alias = schema_editor.connection.alias
    
    # Check if api_cacaoimage table exists
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'api_cacaoimage'
            );
        """)
        api_image_exists = cursor.fetchone()[0]
        
        if not api_image_exists:
            # Tables don't exist, nothing to migrate
            return
        
        # Check if there's any data in api_cacaoimage
        cursor.execute("SELECT COUNT(*) FROM api_cacaoimage;")
        api_image_count = cursor.fetchone()[0]
        
        if api_image_count == 0:
            # No data to migrate
            return
        
        # Migrate CacaoImage data
        # Map fields from api_cacaoimage to images_app_cacaoimage
        # Note: Some fields may have changed, so we map what we can
        cursor.execute("""
            INSERT INTO images_app_cacaoimage (
                id, created_at, updated_at, image, uploaded_at, processed,
                notas, file_name, file_size, file_type, user_id, lote_id
            )
            SELECT 
                id, created_at, updated_at, image, uploaded_at, processed,
                COALESCE(notas, ''), file_name, file_size, file_type, user_id, NULL
            FROM api_cacaoimage
            WHERE id NOT IN (SELECT id FROM images_app_cacaoimage)
            ON CONFLICT (id) DO NOTHING;
        """)
        
        # Migrate CacaoPrediction data
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'api_cacaoprediction'
            );
        """)
        api_prediction_exists = cursor.fetchone()[0]
        
        if api_prediction_exists:
            cursor.execute("""
                INSERT INTO images_app_cacaoprediction (
                    id, image_id, user_id, alto_mm, ancho_mm, grosor_mm, peso_g,
                    confidence_alto, confidence_ancho, confidence_grosor, confidence_peso,
                    processing_time_ms, crop_url, model_version, device_used, created_at,
                    quality_score, maturity_percentage, defects_count, analysis_status, processing_time
                )
                SELECT 
                    id, image_id, NULL, alto_mm, ancho_mm, grosor_mm, peso_g,
                    confidence_alto, confidence_ancho, confidence_grosor, confidence_peso,
                    processing_time_ms, crop_url, model_version, device_used, created_at,
                    NULL, NULL, 0, 'completed', NULL
                FROM api_cacaoprediction
                WHERE image_id IN (SELECT id FROM images_app_cacaoimage)
                AND image_id NOT IN (SELECT image_id FROM images_app_cacaoprediction WHERE image_id IS NOT NULL)
                ON CONFLICT (image_id) DO NOTHING;
            """)


def migrate_cacao_data_reverse(apps, schema_editor):
    """
    Reverse migration - not implemented as we're removing duplicate tables.
    """
    pass


def remove_duplicate_tables_forward(apps, schema_editor):
    """
    Remove the duplicate api_cacaoimage and api_cacaoprediction tables.
    """
    db_alias = schema_editor.connection.alias
    
    with schema_editor.connection.cursor() as cursor:
        # Check if tables exist before trying to drop them
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'api_cacaoprediction'
            );
        """)
        if cursor.fetchone()[0]:
            cursor.execute("DROP TABLE IF EXISTS api_cacaoprediction CASCADE;")
        
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'api_cacaoimage'
            );
        """)
        if cursor.fetchone()[0]:
            cursor.execute("DROP TABLE IF EXISTS api_cacaoimage CASCADE;")


def remove_duplicate_tables_reverse(apps, schema_editor):
    """
    Reverse migration - not implemented as we don't want to recreate duplicate tables.
    """
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0019_merge_0016_remove_tables'),
        ('images_app', '0001_initial'),  # Ensure images_app tables exist
    ]

    operations = [
        # First, migrate any existing data from api tables to images_app tables
        migrations.RunPython(
            migrate_cacao_data_forward,
            reverse_code=migrate_cacao_data_reverse,
        ),
        # Then, remove the duplicate tables
        migrations.RunPython(
            remove_duplicate_tables_forward,
            reverse_code=remove_duplicate_tables_reverse,
        ),
    ]

