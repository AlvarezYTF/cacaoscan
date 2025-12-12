# Generated migration to normalize ReporteGenerado with catalogs
# -*- coding: utf-8 -*-
from django.db import migrations, models
import django.db.models.deletion


def normalize_reportegenerado_data(apps, schema_editor):
    """Migrate ReporteGenerado data from CharField to ForeignKeys to Parametro."""
    ReporteGenerado = apps.get_model('reports', 'ReporteGenerado')
    Parametro = apps.get_model('catalogos', 'Parametro')
    Tema = apps.get_model('catalogos', 'Tema')
    
    # Get themes
    try:
        tema_tipo_reporte = Tema.objects.get(codigo='TEMA_TIPO_REPORTE')
        tema_formato_reporte = Tema.objects.get(codigo='TEMA_FORMATO_REPORTE')
        tema_estado_reporte = Tema.objects.get(codigo='TEMA_ESTADO_REPORTE')
    except Tema.DoesNotExist:
        print("WARNING: Required themes not found. Skipping ReporteGenerado catalog migration.")
        return
    
    # Mapping functions
    def find_tipo_reporte(value):
        """Find Parametro (TEMA_TIPO_REPORTE) by code (case insensitive)."""
        if not value:
            return None
        value_upper = value.upper().strip()
        # Map old choices to new codes
        mapping = {
            'calidad': 'CALIDAD',
            'defectos': 'DEFECTOS',
            'rendimiento': 'RENDIMIENTO',
            'finca': 'FINCA',
            'lote': 'LOTE',
            'usuario': 'USUARIO',
            'auditoria': 'AUDITORIA',
            'personalizado': 'PERSONALIZADO',
            'analisis_periodo': 'ANALISIS_PERIODO',
        }
        codigo = mapping.get(value.lower(), value_upper)
        try:
            return Parametro.objects.get(tema=tema_tipo_reporte, codigo=codigo)
        except Parametro.DoesNotExist:
            # Default to CALIDAD if exists
            return Parametro.objects.filter(tema=tema_tipo_reporte, codigo='CALIDAD').first()
    
    def find_formato_reporte(value):
        """Find Parametro (TEMA_FORMATO_REPORTE) by code (case insensitive)."""
        if not value:
            return None
        value_upper = value.upper().strip()
        try:
            return Parametro.objects.get(tema=tema_formato_reporte, codigo=value_upper)
        except Parametro.DoesNotExist:
            # Default to PDF if exists
            return Parametro.objects.filter(tema=tema_formato_reporte, codigo='PDF').first()
    
    def find_estado_reporte(value):
        """Find Parametro (TEMA_ESTADO_REPORTE) by code (case insensitive)."""
        if not value:
            return None
        value_upper = value.upper().strip()
        # Map old choices to new codes
        mapping = {
            'pendiente': 'PENDIENTE',
            'generando': 'GENERANDO',
            'completado': 'COMPLETADO',
            'fallido': 'FALLIDO',
            'expirado': 'EXPIRADO',
        }
        codigo = mapping.get(value.lower(), value_upper)
        try:
            return Parametro.objects.get(tema=tema_estado_reporte, codigo=codigo)
        except Parametro.DoesNotExist:
            # Default to PENDIENTE if exists
            return Parametro.objects.filter(tema=tema_estado_reporte, codigo='PENDIENTE').first()
    
    # Migrate data
    reportes = ReporteGenerado.objects.all()
    migrated_tipo = 0
    migrated_formato = 0
    migrated_estado = 0
    
    for reporte in reportes:
        # Migrate tipo_reporte (from CharField to temporary FK)
        tipo_value = getattr(reporte, 'tipo_reporte', None)
        if tipo_value and isinstance(tipo_value, str):
            tipo_obj = find_tipo_reporte(tipo_value)
            if tipo_obj:
                reporte.tipo_reporte_fk_id = tipo_obj.id
                migrated_tipo += 1
        
        # Migrate formato (from CharField to temporary FK)
        formato_value = getattr(reporte, 'formato', None)
        if formato_value and isinstance(formato_value, str):
            formato_obj = find_formato_reporte(formato_value)
            if formato_obj:
                reporte.formato_fk_id = formato_obj.id
                migrated_formato += 1
        
        # Migrate estado (from CharField to temporary FK)
        estado_value = getattr(reporte, 'estado', None)
        if estado_value and isinstance(estado_value, str):
            estado_obj = find_estado_reporte(estado_value)
            if estado_obj:
                reporte.estado_fk_id = estado_obj.id
                migrated_estado += 1
        
        reporte.save(update_fields=['tipo_reporte_fk_id', 'formato_fk_id', 'estado_fk_id'])
    
    print(f"Migrated {migrated_tipo} tipo_reporte, {migrated_formato} formato, {migrated_estado} estado")


def reverse_normalize_reportegenerado_data(apps, schema_editor):
    """Reverse migration - convert ForeignKeys back to CharField."""
    ReporteGenerado = apps.get_model('reports', 'ReporteGenerado')
    # This is a one-way migration - we don't reverse it
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0006_reportegenerado_ruta_archivo_and_more'),
        ('catalogos', '0013_create_themes_and_migrate_catalogs'),  # Use unified catalog system
    ]

    operations = [
        # Add temporary ForeignKey columns with different names
        migrations.AddField(
            model_name='reportegenerado',
            name='tipo_reporte_fk',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='reportes_temp',
                to='catalogos.parametro',
                limit_choices_to={'tema__codigo': 'TEMA_TIPO_REPORTE'},
                help_text='Tipo de reporte (temporal)'
            ),
        ),
        migrations.AddField(
            model_name='reportegenerado',
            name='formato_fk',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='reportes_temp_formato',
                to='catalogos.parametro',
                limit_choices_to={'tema__codigo': 'TEMA_FORMATO_REPORTE'},
                help_text='Formato del reporte (temporal)'
            ),
        ),
        migrations.AddField(
            model_name='reportegenerado',
            name='estado_fk',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='reportes_temp_estado',
                to='catalogos.parametro',
                limit_choices_to={'tema__codigo': 'TEMA_ESTADO_REPORTE'},
                help_text='Estado del reporte (temporal)'
            ),
        ),
        # Migrate data (using temporary column names)
        migrations.RunPython(
            normalize_reportegenerado_data,
            reverse_normalize_reportegenerado_data,
        ),
        # Remove old CharField columns
        migrations.RemoveField(
            model_name='reportegenerado',
            name='tipo_reporte',
        ),
        migrations.RemoveField(
            model_name='reportegenerado',
            name='formato',
        ),
        migrations.RemoveField(
            model_name='reportegenerado',
            name='estado',
        ),
        # Rename temporary ForeignKey columns to final names
        migrations.RenameField(
            model_name='reportegenerado',
            old_name='tipo_reporte_fk',
            new_name='tipo_reporte',
        ),
        migrations.RenameField(
            model_name='reportegenerado',
            old_name='formato_fk',
            new_name='formato',
        ),
        migrations.RenameField(
            model_name='reportegenerado',
            old_name='estado_fk',
            new_name='estado',
        ),
        # Update related_name and make fields NOT NULL
        migrations.AlterField(
            model_name='reportegenerado',
            name='tipo_reporte',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='reportes',
                to='catalogos.parametro',
                limit_choices_to={'tema__codigo': 'TEMA_TIPO_REPORTE'},
                help_text='Tipo de reporte'
            ),
        ),
        migrations.AlterField(
            model_name='reportegenerado',
            name='formato',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='reportes',
                to='catalogos.parametro',
                limit_choices_to={'tema__codigo': 'TEMA_FORMATO_REPORTE'},
                help_text='Formato del reporte'
            ),
        ),
        migrations.AlterField(
            model_name='reportegenerado',
            name='estado',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='reportes',
                to='catalogos.parametro',
                limit_choices_to={'tema__codigo': 'TEMA_ESTADO_REPORTE'},
                help_text='Estado del reporte'
            ),
        ),
        # Add indexes
        migrations.AddIndex(
            model_name='reportegenerado',
            index=models.Index(fields=['tipo_reporte'], name='api_reportegenerado_tipo_reporte_idx'),
        ),
        migrations.AddIndex(
            model_name='reportegenerado',
            index=models.Index(fields=['formato'], name='api_reportegenerado_formato_idx'),
        ),
        migrations.AddIndex(
            model_name='reportegenerado',
            index=models.Index(fields=['estado'], name='api_reportegenerado_estado_idx'),
        ),
    ]

