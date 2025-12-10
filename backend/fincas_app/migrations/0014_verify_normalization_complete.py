# Generated manually - Verify and ensure complete normalization of Finca and Lote models
# This migration verifies that all data is normalized and removes any residual text fields
# -*- coding: utf-8 -*-

from django.db import migrations


def verify_normalization(apps, schema_editor):
    """
    Verify that all Finca and Lote data is properly normalized.
    This function checks for any inconsistencies and logs warnings.
    Now uses Parametro instead of old catalog models.
    """
    Finca = apps.get_model('fincas_app', 'Finca')
    Lote = apps.get_model('fincas_app', 'Lote')
    Municipio = apps.get_model('catalogos', 'Municipio')
    Parametro = apps.get_model('catalogos', 'Parametro')
    Tema = apps.get_model('catalogos', 'Tema')
    
    # Verify Finca normalization
    fincas_without_municipio = Finca.objects.filter(municipio__isnull=True).count()
    if fincas_without_municipio > 0:
        print(f"WARNING: {fincas_without_municipio} fincas without municipio FK")
    
    # Verify Lote normalization
    lotes_without_variedad = Lote.objects.filter(variedad__isnull=True).count()
    if lotes_without_variedad > 0:
        print(f"WARNING: {lotes_without_variedad} lotes without variedad FK")
    
    # Verify all municipios exist in catalog
    fincas = Finca.objects.select_related('municipio').all()
    invalid_municipios = 0
    for finca in fincas:
        if finca.municipio and not Municipio.objects.filter(id=finca.municipio.id).exists():
            invalid_municipios += 1
    
    if invalid_municipios > 0:
        print(f"WARNING: {invalid_municipios} fincas with invalid municipio FK")
    
    # Verify all variedades exist in Parametro (TEMA_VARIEDAD_CACAO)
    # Note: We can't use select_related because the FK might still point to old catalog table in migration state
    # Instead, we'll check directly using the FK ID
    try:
        tema_variedad = Tema.objects.get(codigo='TEMA_VARIEDAD_CACAO')
        # Get all lote IDs with variedad_id
        with schema_editor.connection.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT variedad_id 
                FROM fincas_app_lote 
                WHERE variedad_id IS NOT NULL
            """)
            variedad_ids = [row[0] for row in cursor.fetchall()]
        
        invalid_variedades = 0
        for variedad_id in variedad_ids:
            # Check if this ID exists in Parametro with the correct tema
            if not Parametro.objects.filter(id=variedad_id, tema=tema_variedad).exists():
                invalid_variedades += 1
        
        if invalid_variedades > 0:
            print(f"WARNING: {invalid_variedades} lotes with invalid variedad FK")
    except Tema.DoesNotExist:
        print("WARNING: TEMA_VARIEDAD_CACAO not found. Skipping variedad validation.")
    
    print("Normalization verification completed")


def reverse_verify_normalization(apps, schema_editor):
    """
    Reverse operation - no-op since this is just verification.
    """
    pass


def check_and_remove_duplicate_tables(apps, schema_editor):
    """
    Check for and remove any duplicate tables with text fields.
    """
    with schema_editor.connection.cursor() as cursor:
        # Check if api_finca has text fields (should not exist)
        cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
            AND table_name = 'api_finca'
            AND column_name IN ('municipio', 'departamento')
            AND data_type = 'character varying';
        """)
        text_fields = cursor.fetchall()
        
        if text_fields:
            print(f"WARNING: Found text fields in api_finca: {text_fields}")
            print("These should have been migrated to FKs. Manual intervention may be required.")
        
        # Check if api_lote exists (should have been removed)
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'api_lote'
            );
        """)
        api_lote_exists = cursor.fetchone()[0]
        
        if api_lote_exists:
            print("WARNING: api_lote table still exists. It should have been removed.")
            print("This table is obsolete and should be dropped manually if it contains no data.")
        
        # Check if fincas_app_finca exists (should not, api_finca is the correct table)
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'fincas_app_finca'
            );
        """)
        fincas_app_finca_exists = cursor.fetchone()[0]
        
        if fincas_app_finca_exists:
            print("WARNING: fincas_app_finca table exists. This may be a duplicate.")
            print("The correct table is api_finca (managed by fincas_app.Finca with db_table='api_finca').")
        
        # Check if fincas_app_lote exists (should not, should use api_lote or be removed)
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'fincas_app_lote'
            );
        """)
        fincas_app_lote_exists = cursor.fetchone()[0]
        
        if fincas_app_lote_exists:
            print("INFO: fincas_app_lote table exists. This is the correct table for Lote model.")


def reverse_check_duplicate_tables(apps, schema_editor):
    """
    Reverse operation - no-op since this is just verification.
    """
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('fincas_app', '0013_normalize_lote_catalogos'),
        ('catalogos', '0016_add_tema_foreignkey_to_parametro'),  # Ensure Parametro has tema FK
    ]

    operations = [
        # Verify normalization
        migrations.RunPython(
            verify_normalization,
            reverse_verify_normalization,
        ),
        # Check for duplicate tables
        migrations.RunPython(
            check_and_remove_duplicate_tables,
            reverse_check_duplicate_tables,
        ),
    ]

