# Generated manually - Migrate data from api_cacaoimage to images_app_cacaoimage
# -*- coding: utf-8 -*-

from django.db import migrations


def migrate_api_cacaoimage_data(apps, schema_editor):
    """
    Migrate data from api_cacaoimage to images_app_cacaoimage.
    Maps text fields (finca, region, variedad) to metadata JSON field.
    Uses SQL direct for efficiency and to handle JSON metadata properly.
    """
    import json
    
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
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            # Table doesn't exist, nothing to migrate
            return
        
        # Check if images_app_cacaoimage table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'images_app_cacaoimage'
            );
        """)
        target_table_exists = cursor.fetchone()[0]
        
        if not target_table_exists:
            # Target table doesn't exist yet, skip migration
            return
        
        # Get all records from api_cacaoimage
        cursor.execute("""
            SELECT 
                id, user_id, image, uploaded_at, processed,
                finca, region, lote_id, variedad, fecha_cosecha,
                notas, file_name, file_size, file_type,
                created_at, updated_at, metadata
            FROM api_cacaoimage
            ORDER BY id;
        """)
        
        api_images = cursor.fetchall()
        
        if not api_images:
            # No data to migrate
            return
        
        # Migrate each image using SQL INSERT
        for api_img in api_images:
            (api_id, user_id, image_path, uploaded_at, processed,
             finca_text, region_text, lote_id_text, variedad_text, fecha_cosecha,
             notas, file_name, file_size, file_type,
             created_at, updated_at, metadata_json) = api_img
            
            # Build metadata from text fields
            metadata = {}
            if metadata_json:
                try:
                    if isinstance(metadata_json, dict):
                        metadata = metadata_json
                    else:
                        metadata = json.loads(metadata_json) if isinstance(metadata_json, str) else {}
                except (json.JSONDecodeError, TypeError):
                    metadata = {}
            
            # Add text fields to metadata if they exist and aren't already in metadata
            if finca_text and 'finca' not in metadata:
                metadata['finca'] = finca_text
            if region_text and 'region' not in metadata:
                metadata['region'] = region_text
            if variedad_text and 'variedad' not in metadata:
                metadata['variedad'] = variedad_text
            if fecha_cosecha:
                if 'fecha_cosecha' not in metadata:
                    if hasattr(fecha_cosecha, 'isoformat'):
                        metadata['fecha_cosecha'] = fecha_cosecha.isoformat()
                    else:
                        metadata['fecha_cosecha'] = str(fecha_cosecha)
            
            # Try to find lote by ID (if lote_id_text is a number)
            lote_id_value = None
            if lote_id_text:
                try:
                    lote_id_int = int(lote_id_text)
                    # Check if lote exists in fincas_app_lote
                    cursor.execute("""
                        SELECT id FROM fincas_app_lote WHERE id = %s;
                    """, [lote_id_int])
                    lote_result = cursor.fetchone()
                    if lote_result:
                        lote_id_value = lote_id_int
                    else:
                        # Lote not found, keep lote_id in metadata
                        metadata['lote_id_original'] = lote_id_text
                except (ValueError, TypeError):
                    # lote_id_text is not a number, keep in metadata
                    metadata['lote_id_original'] = lote_id_text
            
            # Convert metadata to JSON string
            metadata_json_str = json.dumps(metadata) if metadata else '{}'
            
            # Insert into images_app_cacaoimage
            cursor.execute("""
                INSERT INTO images_app_cacaoimage (
                    user_id, image, uploaded_at, processed,
                    lote_id, notas, file_name, file_size, file_type,
                    created_at, updated_at, metadata
                ) VALUES (
                    %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s::jsonb
                );
            """, [
                user_id, image_path, uploaded_at, processed,
                lote_id_value, notas or "", file_name or "", file_size, file_type or "",
                created_at, updated_at, metadata_json_str
            ])


def reverse_migrate_api_cacaoimage_data(apps, schema_editor):
    """
    Reverse migration - this is a one-way migration.
    Data migration from api_cacaoimage to images_app_cacaoimage cannot be safely reversed.
    """
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('images_app', '0009_add_metadata_field'),
        ('fincas_app', '0013_normalize_lote_catalogos'),
    ]

    operations = [
        migrations.RunPython(
            migrate_api_cacaoimage_data,
            reverse_migrate_api_cacaoimage_data,
        ),
    ]

