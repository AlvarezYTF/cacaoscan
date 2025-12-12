# Generated manually - Final 2NF verification and cleanup for Lote model
# This migration ensures that api_lote (if exists) is properly removed
# and that all Lote data uses ForeignKeys for variedad and estado
# -*- coding: utf-8 -*-

from django.db import migrations


def verify_2nf_compliance(apps, schema_editor):
    """
    Verify that Lote model complies with 2NF:
    - variedad must be ForeignKey to Parametro (TEMA_VARIEDAD_CACAO) (not CharField)
    - estado must be ForeignKey to Parametro (TEMA_ESTADO_LOTE) (not CharField)
    - api_lote table should not exist (obsolete)
    """
    with schema_editor.connection.cursor() as cursor:
        # Check if api_lote table still exists (should not)
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'api_lote'
            );
        """)
        api_lote_exists = cursor.fetchone()[0]
        
        if api_lote_exists:
            print("WARNING: api_lote table still exists!")
            print("This table is obsolete and violates 2NF.")
            print("Checking if it has data...")
            
            cursor.execute("SELECT COUNT(*) FROM api_lote;")
            count = cursor.fetchone()[0]
            
            if count > 0:
                print(f"WARNING: api_lote has {count} records!")
                print("These should have been migrated to fincas_app_lote.")
                print("Manual data migration may be required.")
            else:
                print("api_lote is empty. It can be safely dropped.")
        
        # Check if fincas_app_lote has text fields for variedad or estado
        cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
            AND table_name = 'fincas_app_lote'
            AND column_name IN ('variedad', 'estado')
            AND data_type = 'character varying';
        """)
        text_fields = cursor.fetchall()
        
        if text_fields:
            print(f"ERROR: fincas_app_lote still has text fields: {text_fields}")
            print("These violate 2NF and should be ForeignKeys!")
            print("The migration 0013_normalize_lote_catalogos should have fixed this.")
            raise Exception("2NF violation detected: text fields found in fincas_app_lote")
        
        # Verify that variedad and estado are ForeignKeys
        cursor.execute("""
            SELECT 
                column_name,
                data_type,
                udt_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
            AND table_name = 'fincas_app_lote'
            AND column_name IN ('variedad_id', 'estado_id');
        """)
        fk_fields = cursor.fetchall()
        
        if not fk_fields or len(fk_fields) < 1:
            print("WARNING: Could not find variedad_id or estado_id ForeignKey columns!")
            print("This suggests the normalization migration may not have run correctly.")
        else:
            print(f"✓ Found ForeignKey columns: {fk_fields}")
            print("✓ 2NF compliance verified: variedad and estado are ForeignKeys")
        
        # Check for any lotes without variedad FK (should not exist)
        cursor.execute("""
            SELECT COUNT(*) 
            FROM fincas_app_lote 
            WHERE variedad_id IS NULL;
        """)
        null_variedad = cursor.fetchone()[0]
        
        if null_variedad > 0:
            print(f"WARNING: {null_variedad} lotes have NULL variedad_id")
            print("These should have a valid ForeignKey to Parametro (TEMA_VARIEDAD_CACAO)")
        
        # Check for any lotes with invalid variedad FK
        # Now variedad_id should point to catalogos_parametro with tema TEMA_VARIEDAD_CACAO
        cursor.execute("""
            SELECT COUNT(*) 
            FROM fincas_app_lote l
            WHERE l.variedad_id IS NOT NULL
            AND NOT EXISTS (
                SELECT 1 FROM catalogos_parametro p
                INNER JOIN catalogos_tema t ON p.tema_id = t.id
                WHERE p.id = l.variedad_id
                AND t.codigo = 'TEMA_VARIEDAD_CACAO'
            );
        """)
        invalid_variedad = cursor.fetchone()[0]
        
        if invalid_variedad > 0:
            print(f"ERROR: {invalid_variedad} lotes have invalid variedad_id ForeignKey!")
            print("These violate referential integrity.")
        
        # Check for any lotes with invalid estado FK (if estado_id is not NULL)
        # Now estado_id should point to catalogos_parametro with tema TEMA_ESTADO_LOTE
        cursor.execute("""
            SELECT COUNT(*) 
            FROM fincas_app_lote l
            WHERE l.estado_id IS NOT NULL
            AND NOT EXISTS (
                SELECT 1 FROM catalogos_parametro p
                INNER JOIN catalogos_tema t ON p.tema_id = t.id
                WHERE p.id = l.estado_id
                AND t.codigo = 'TEMA_ESTADO_LOTE'
            );
        """)
        invalid_estado = cursor.fetchone()[0]
        
        if invalid_estado > 0:
            print(f"ERROR: {invalid_estado} lotes have invalid estado_id ForeignKey!")
            print("These violate referential integrity.")
        
        print("\n=== 2NF Verification Summary ===")
        if api_lote_exists:
            print("❌ api_lote table still exists (should be removed)")
        else:
            print("✓ api_lote table does not exist")
        
        if text_fields:
            print("❌ Text fields found in fincas_app_lote (2NF violation)")
        else:
            print("✓ No text fields in fincas_app_lote")
        
        if fk_fields and len(fk_fields) >= 1:
            print("✓ ForeignKey columns found (2NF compliant)")
        else:
            print("❌ ForeignKey columns missing (2NF violation)")
        
        if null_variedad == 0 and invalid_variedad == 0 and invalid_estado == 0:
            print("✓ All ForeignKeys are valid")
            print("\n✅ 2NF compliance verified for Lote model!")
        else:
            print(f"\n⚠️  Found {null_variedad + invalid_variedad + invalid_estado} data inconsistencies")


def cleanup_api_lote_if_empty(apps, schema_editor):
    """
    If api_lote exists and is empty, drop it.
    """
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'api_lote'
            );
        """)
        api_lote_exists = cursor.fetchone()[0]
        
        if not api_lote_exists:
            return
        
        # Check if empty
        cursor.execute("SELECT COUNT(*) FROM api_lote;")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("api_lote is empty, dropping it...")
            # Drop constraints and indexes first
            cursor.execute("""
                DO $$ 
                DECLARE
                    r RECORD;
                BEGIN
                    FOR r IN (SELECT constraint_name FROM information_schema.table_constraints 
                             WHERE table_name = 'api_lote' AND constraint_type = 'FOREIGN KEY')
                    LOOP
                        EXECUTE 'ALTER TABLE api_lote DROP CONSTRAINT IF EXISTS ' || quote_ident(r.constraint_name) || ' CASCADE';
                    END LOOP;
                END $$;
            """)
            
            cursor.execute("DROP TABLE IF EXISTS api_lote CASCADE;")
            print("✓ Dropped empty api_lote table")
        else:
            print(f"⚠️  api_lote has {count} records. Manual migration required.")


def reverse_verify_2nf_compliance(apps, schema_editor):
    """
    Reverse operation - no-op since this is just verification.
    """
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('fincas_app', '0018_remove_finca_api_finca_agricul_8d1606_idx_and_more'),
        ('catalogos', '0016_add_tema_foreignkey_to_parametro'),  # Ensure Parametro has tema field
    ]

    operations = [
        migrations.RunPython(
            verify_2nf_compliance,
            reverse_verify_2nf_compliance,
        ),
        migrations.RunPython(
            cleanup_api_lote_if_empty,
            reverse_verify_2nf_compliance,
        ),
    ]

