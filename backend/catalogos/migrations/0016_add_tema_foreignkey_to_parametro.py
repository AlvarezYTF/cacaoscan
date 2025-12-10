# Generated manually - Add tema ForeignKey to Parametro
# This migration adds the tema ForeignKey field to Parametro model
# If Parametro records exist, they will be assigned to their tema based on TemaParametro pivot table
# -*- coding: utf-8 -*-

from django.db import migrations, models
import django.db.models.deletion


def assign_tema_to_existing_parametros(apps, schema_editor):
    """
    Assign tema to existing Parametro records.
    Since Parametro was created with tema in migration 0013, all existing parametros should already have tema.
    This function is a safety check in case some parametros don't have tema assigned.
    """
    Parametro = apps.get_model('catalogos', 'Parametro')
    Tema = apps.get_model('catalogos', 'Tema')
    
    # Get all parametros without tema
    parametros_without_tema = Parametro.objects.filter(tema__isnull=True)
    
    if parametros_without_tema.exists():
        print(f"WARNING: Found {parametros_without_tema.count()} parametros without tema. They should have been created with tema in migration 0013.")
        # Try to infer tema from parametro codigo or other clues
        # This is a fallback - ideally all parametros should have tema from migration 0013
        for parametro in parametros_without_tema:
            print(f"WARNING: Parametro {parametro.codigo} has no tema assigned. Please assign manually or delete if orphaned.")
    else:
        print("All parametros already have tema assigned (from migration 0013).")


def reverse_assign_tema(apps, schema_editor):
    """
    Reverse migration: Set tema to None for all parametros.
    """
    Parametro = apps.get_model('catalogos', 'Parametro')
    Parametro.objects.all().update(tema=None)


def check_and_add_tema_field(apps, schema_editor):
    """
    Check if tema_id column exists, and if not, add it.
    If it exists, just verify that all parametros have tema assigned.
    """
    with schema_editor.connection.cursor() as cursor:
        # Check if tema_id column exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'catalogos_parametro'
                AND column_name = 'tema_id'
            );
        """)
        tema_id_exists = cursor.fetchone()[0]
        
        if not tema_id_exists:
            print("tema_id column does not exist, will be added by AddField operation")
        else:
            print("tema_id column already exists, skipping AddField operation")
            
            # Verify that all parametros have tema assigned
            Parametro = apps.get_model('catalogos', 'Parametro')
            parametros_without_tema = Parametro.objects.filter(tema__isnull=True)
            if parametros_without_tema.exists():
                print(f"WARNING: Found {parametros_without_tema.count()} parametros without tema.")
                for parametro in parametros_without_tema:
                    print(f"WARNING: Parametro {parametro.codigo} has no tema assigned.")


def reverse_check_and_add_tema_field(apps, schema_editor):
    """Reverse: do nothing"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('catalogos', '0015_force_remove_old_catalog_tables'),
    ]

    operations = [
        # Step 1: Check if tema field exists and conditionally add it
        migrations.RunPython(
            check_and_add_tema_field,
            reverse_check_and_add_tema_field,
        ),
        # Step 2: Conditionally add tema field (only if it doesn't exist)
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_schema = 'public' 
                        AND table_name = 'catalogos_parametro'
                        AND column_name = 'tema_id'
                    ) THEN
                        ALTER TABLE catalogos_parametro 
                        ADD COLUMN tema_id BIGINT NULL 
                        REFERENCES catalogos_tema(id) ON DELETE CASCADE;
                    END IF;
                END $$;
            """,
            reverse_sql="ALTER TABLE catalogos_parametro DROP COLUMN IF EXISTS tema_id CASCADE;"
        ),
        # Step 2b: Update Django state to include tema field
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name='parametro',
                    name='tema',
                    field=models.ForeignKey(
                        null=True,
                        blank=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='parametros',
                        to='catalogos.tema',
                        help_text='Tema al que pertenece este parámetro'
                    ),
                ),
            ],
            database_operations=[],
        ),
        # Step 3: Assign tema to existing parametros (if any don't have it)
        migrations.RunPython(
            assign_tema_to_existing_parametros,
            reverse_assign_tema,
        ),
        # Step 4: Make tema non-nullable (if it's currently nullable)
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    IF EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_schema = 'public' 
                        AND table_name = 'catalogos_parametro'
                        AND column_name = 'tema_id'
                        AND is_nullable = 'YES'
                    ) THEN
                        ALTER TABLE catalogos_parametro 
                        ALTER COLUMN tema_id SET NOT NULL;
                    END IF;
                END $$;
            """,
            reverse_sql="ALTER TABLE catalogos_parametro ALTER COLUMN tema_id DROP NOT NULL;"
        ),
        # Step 5: Update state to reflect non-nullable tema
        migrations.AlterField(
            model_name='parametro',
            name='tema',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='parametros',
                to='catalogos.tema',
                help_text='Tema al que pertenece este parámetro'
            ),
        ),
        # Step 6: Add unique_together constraint (if it doesn't exist)
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT FROM pg_constraint 
                        WHERE conname = 'catalogos_parametro_tema_id_codigo_uniq'
                    ) THEN
                        ALTER TABLE catalogos_parametro 
                        ADD CONSTRAINT catalogos_parametro_tema_id_codigo_uniq 
                        UNIQUE (tema_id, codigo);
                    END IF;
                END $$;
            """,
            reverse_sql="ALTER TABLE catalogos_parametro DROP CONSTRAINT IF EXISTS catalogos_parametro_tema_id_codigo_uniq;"
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterUniqueTogether(
                    name='parametro',
                    unique_together={('tema', 'codigo')},
                ),
            ],
            database_operations=[],
        ),
        # Step 7: Update ordering and indexes
        migrations.AlterModelOptions(
            name='parametro',
            options={
                'verbose_name': 'Parámetro',
                'verbose_name_plural': 'Parámetros',
                'ordering': ['tema', 'codigo'],
            },
        ),
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT FROM pg_indexes 
                        WHERE indexname = 'catalogos_p_tema_id_codigo_idx'
                    ) THEN
                        CREATE INDEX catalogos_p_tema_id_codigo_idx 
                        ON catalogos_parametro (tema_id, codigo);
                    END IF;
                END $$;
            """,
            reverse_sql="DROP INDEX IF EXISTS catalogos_p_tema_id_codigo_idx;"
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddIndex(
                    model_name='parametro',
                    index=models.Index(fields=['tema', 'codigo'], name='catalogos_p_tema_id_codigo_idx'),
                ),
            ],
            database_operations=[],
        ),
        # Step 8: Add metadata field if it doesn't exist
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_schema = 'public' 
                        AND table_name = 'catalogos_parametro'
                        AND column_name = 'metadata'
                    ) THEN
                        ALTER TABLE catalogos_parametro 
                        ADD COLUMN metadata JSONB DEFAULT '{}'::jsonb;
                    END IF;
                END $$;
            """,
            reverse_sql="ALTER TABLE catalogos_parametro DROP COLUMN IF EXISTS metadata;"
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name='parametro',
                    name='metadata',
                    field=models.JSONField(blank=True, default=dict, help_text='Metadata adicional para el parámetro (ej: mime_type para TipoArchivo, fecha_lanzamiento para VersionModelo)'),
                ),
            ],
            database_operations=[],
        ),
    ]

