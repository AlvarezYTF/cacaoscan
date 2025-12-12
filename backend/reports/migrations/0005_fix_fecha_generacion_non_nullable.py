# Generated manually - Fix fecha_generacion field to be non-nullable with auto_now_add
# This migration handles the change from nullable to non-nullable

from django.db import migrations, models
from django.utils import timezone


def populate_fecha_generacion(apps, schema_editor):
    """Populate fecha_generacion for existing records that have NULL values."""
    ReporteGenerado = apps.get_model('reports', 'ReporteGenerado')
    
    # Update records where fecha_generacion is NULL
    # Use fecha_solicitud if available, otherwise use current time
    for reporte in ReporteGenerado.objects.filter(fecha_generacion__isnull=True):
        if reporte.fecha_solicitud:
            reporte.fecha_generacion = reporte.fecha_solicitud
        else:
            reporte.fecha_generacion = timezone.now()
        reporte.save(update_fields=['fecha_generacion'])


def reverse_populate_fecha_generacion(apps, schema_editor):
    """Reverse migration - no action needed."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0004_fix_non_nullable_fields_temporary_defaults'),
    ]

    operations = [
        # First, populate existing NULL values
        migrations.RunPython(
            populate_fecha_generacion,
            reverse_populate_fecha_generacion
        ),
        # Then, change the field to non-nullable with auto_now_add
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name='reportegenerado',
                    name='fecha_generacion',
                    field=models.DateTimeField(
                        auto_now_add=True,
                        help_text='Fecha de generación del reporte'
                    ),
                ),
            ],
            database_operations=[
                # Update database: remove null constraint and add default
                migrations.RunSQL(
                    sql="""
                        DO $$
                        BEGIN
                            -- Set default for NULL values (shouldn't be any after RunPython)
                            UPDATE api_reportegenerado 
                            SET fecha_generacion = fecha_solicitud 
                            WHERE fecha_generacion IS NULL;
                            
                            -- Make column NOT NULL
                            ALTER TABLE api_reportegenerado 
                            ALTER COLUMN fecha_generacion SET NOT NULL;
                            
                            -- Add default for future inserts (auto_now_add behavior)
                            ALTER TABLE api_reportegenerado 
                            ALTER COLUMN fecha_generacion SET DEFAULT CURRENT_TIMESTAMP;
                        END $$;
                    """,
                    reverse_sql="""
                        ALTER TABLE api_reportegenerado 
                        ALTER COLUMN fecha_generacion DROP NOT NULL;
                        ALTER TABLE api_reportegenerado 
                        ALTER COLUMN fecha_generacion DROP DEFAULT;
                    """,
                ),
            ],
        ),
    ]

