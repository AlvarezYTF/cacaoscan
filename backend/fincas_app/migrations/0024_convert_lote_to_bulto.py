# Generated migration to convert Lote from physical location to grain batch

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalogos', '0001_initial'),
        ('fincas_app', '0023_alter_finca_clima_alter_finca_estado_and_more'),
    ]

    operations = [
        # Step 1: Add new fields as nullable first
        migrations.AddField(
            model_name='lote',
            name='peso_kg',
            field=models.DecimalField(decimal_places=2, help_text='Peso del bulto en kilogramos', max_digits=10, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='lote',
            name='fecha_recepcion',
            field=models.DateField(help_text='Fecha en que se recibió el bulto', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='lote',
            name='fecha_procesamiento',
            field=models.DateField(blank=True, help_text='Fecha de procesamiento/fermentación del bulto (opcional)', null=True),
        ),
        
        # Step 2: Migrate data if needed (migrate fecha_cosecha -> fecha_recepcion, area_hectareas -> peso_kg)
        migrations.RunSQL(
            # Migrate fecha_cosecha to fecha_recepcion if fecha_recepcion is null
            sql="UPDATE fincas_app_lote SET fecha_recepcion = fecha_cosecha WHERE fecha_recepcion IS NULL AND fecha_cosecha IS NOT NULL;",
            reverse_sql="UPDATE fincas_app_lote SET fecha_cosecha = fecha_recepcion WHERE fecha_cosecha IS NULL AND fecha_recepcion IS NOT NULL;"
        ),
        migrations.RunSQL(
            # Migrate area_hectareas to peso_kg (convert hectares to kg - rough estimate: 1 hectare = 1000kg)
            # This is a temporary migration, adjust conversion as needed
            sql="UPDATE fincas_app_lote SET peso_kg = area_hectareas * 1000 WHERE peso_kg IS NULL AND area_hectareas IS NOT NULL;",
            reverse_sql="UPDATE fincas_app_lote SET area_hectareas = peso_kg / 1000 WHERE area_hectareas IS NULL AND peso_kg IS NOT NULL;"
        ),
        
        # Step 3: Make new required fields non-nullable
        migrations.AlterField(
            model_name='lote',
            name='peso_kg',
            field=models.DecimalField(decimal_places=2, help_text='Peso del bulto en kilogramos', max_digits=10),
        ),
        migrations.AlterField(
            model_name='lote',
            name='fecha_recepcion',
            field=models.DateField(help_text='Fecha en que se recibió el bulto'),
        ),
        
        # Step 4: Make fecha_plantacion and fecha_cosecha optional (nullable)
        migrations.AlterField(
            model_name='lote',
            name='fecha_plantacion',
            field=models.DateField(blank=True, help_text='Fecha de plantación del cacao (opcional)', null=True),
        ),
        migrations.AlterField(
            model_name='lote',
            name='fecha_cosecha',
            field=models.DateField(blank=True, help_text='Fecha de cosecha del cacao (opcional)', null=True),
        ),
        
        # Step 5: Remove old fields that are no longer needed
        migrations.RemoveField(
            model_name='lote',
            name='area_hectareas',
        ),
        migrations.RemoveField(
            model_name='lote',
            name='coordenadas_lat',
        ),
        migrations.RemoveField(
            model_name='lote',
            name='coordenadas_lng',
        ),
        migrations.RemoveField(
            model_name='lote',
            name='edad_plantas',
        ),
        
        # Step 6: Remove old constraints (only if they exist)
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    IF EXISTS (
                        SELECT 1 FROM pg_constraint 
                        WHERE conname = 'fincas_app_lote_area_positiva'
                    ) THEN
                        ALTER TABLE fincas_app_lote DROP CONSTRAINT fincas_app_lote_area_positiva;
                    END IF;
                END $$;
            """,
            reverse_sql="-- Cannot reverse constraint removal"
        ),
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    IF EXISTS (
                        SELECT 1 FROM pg_constraint 
                        WHERE conname = 'fincas_app_lote_fecha_cosecha_valida'
                    ) THEN
                        ALTER TABLE fincas_app_lote DROP CONSTRAINT fincas_app_lote_fecha_cosecha_valida;
                    END IF;
                END $$;
            """,
            reverse_sql="-- Cannot reverse constraint removal"
        ),
        
        # Step 7: Add new constraints
        migrations.AddConstraint(
            model_name='lote',
            constraint=models.CheckConstraint(check=models.Q(('peso_kg__gt', 0)), name='fincas_app_lote_peso_positivo'),
        ),
        migrations.AddConstraint(
            model_name='lote',
            constraint=models.CheckConstraint(
                condition=models.Q(('fecha_procesamiento__isnull', True)) | models.Q(('fecha_procesamiento__gte', models.F('fecha_recepcion'))),
                name='fincas_app_lote_fecha_procesamiento_valida'
            ),
        ),
        migrations.AddConstraint(
            model_name='lote',
            constraint=models.CheckConstraint(
                condition=models.Q(('fecha_cosecha__isnull', True)) | models.Q(('fecha_plantacion__isnull', True)) | models.Q(('fecha_cosecha__gte', models.F('fecha_plantacion'))),
                name='fincas_app_lote_fecha_cosecha_valida'
            ),
        ),
    ]

