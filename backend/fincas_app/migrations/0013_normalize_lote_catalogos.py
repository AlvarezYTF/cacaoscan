# Generated migration to normalize Lote model with catalogs
# -*- coding: utf-8 -*-
from django.db import migrations, models
import django.db.models.deletion


def normalize_lote_data(apps, schema_editor):
    """Migrate Lote data from CharField to ForeignKeys to Parametro."""
    Lote = apps.get_model('fincas_app', 'Lote')
    Parametro = apps.get_model('catalogos', 'Parametro')
    Tema = apps.get_model('catalogos', 'Tema')
    
    # Get themes
    try:
        tema_variedad_cacao = Tema.objects.get(codigo='TEMA_VARIEDAD_CACAO')
        tema_estado_lote = Tema.objects.get(codigo='TEMA_ESTADO_LOTE')
    except Tema.DoesNotExist:
        print("WARNING: Required themes not found. Skipping Lote catalog migration.")
        return
    
    # Mapping functions
    def find_variedad(value):
        """Find Parametro (TEMA_VARIEDAD_CACAO) by name (case insensitive)."""
        if not value:
            return None
        value_upper = value.upper().strip()
        # Try exact match first
        try:
            return Parametro.objects.get(tema=tema_variedad_cacao, codigo=value_upper)
        except Parametro.DoesNotExist:
            pass
        # Try by name
        try:
            return Parametro.objects.filter(tema=tema_variedad_cacao, nombre__iexact=value).first()
        except:
            pass
        # Default to FORASTERO if exists
        return Parametro.objects.filter(tema=tema_variedad_cacao, codigo='FORASTERO').first()
    
    def find_estado_lote(value):
        """Find Parametro (TEMA_ESTADO_LOTE) by name (case insensitive)."""
        if not value:
            return None
        value_upper = value.upper().strip()
        # Map common values
        mapping = {
            'activo': 'ACTIVO',
            'inactivo': 'INACTIVO',
            'cosechado': 'COSECHADO',
            'renovado': 'RENOVADO',
        }
        codigo = mapping.get(value_upper, value_upper)
        try:
            return Parametro.objects.get(tema=tema_estado_lote, codigo=codigo)
        except Parametro.DoesNotExist:
            pass
        # Try by name
        try:
            return Parametro.objects.filter(tema=tema_estado_lote, nombre__iexact=value).first()
        except:
            pass
        # Default to ACTIVO if exists
        return Parametro.objects.filter(tema=tema_estado_lote, codigo='ACTIVO').first()
    
    # Migrate data
    lotes = Lote.objects.all()
    migrated_variedad = 0
    migrated_estado = 0
    
    for lote in lotes:
        # Migrate variedad (from CharField to temporary FK)
        variedad_value = getattr(lote, 'variedad', None)
        if variedad_value and isinstance(variedad_value, str):
            variedad_obj = find_variedad(variedad_value)
            if variedad_obj:
                lote.variedad_fk_id = variedad_obj.id
                migrated_variedad += 1
            else:
                # If no match found, use FORASTERO as default
                default_variedad = Parametro.objects.filter(tema=tema_variedad_cacao, codigo='FORASTERO').first()
                if default_variedad:
                    lote.variedad_fk_id = default_variedad.id
                    migrated_variedad += 1
        
        # Migrate estado (from CharField to temporary FK)
        estado_value = getattr(lote, 'estado', None)
        if estado_value and isinstance(estado_value, str):
            estado_obj = find_estado_lote(estado_value)
            if estado_obj:
                lote.estado_fk_id = estado_obj.id
                migrated_estado += 1
        
        lote.save(update_fields=['variedad_fk_id', 'estado_fk_id'])
    
    print(f"Migrated {migrated_variedad} variedad, {migrated_estado} estado")


def reverse_normalize_lote_data(apps, schema_editor):
    """Reverse migration - convert ForeignKeys back to CharField."""
    Lote = apps.get_model('fincas_app', 'Lote')
    # This is a one-way migration - we don't reverse it
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('fincas_app', '0012_normalize_finca_catalogos'),
        ('catalogos', '0013_create_themes_and_migrate_catalogs'),  # Use unified catalog system
    ]

    operations = [
        # Add temporary ForeignKey columns with different names
        migrations.AddField(
            model_name='lote',
            name='variedad_fk',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='lotes_temp',
                to='catalogos.parametro',
                limit_choices_to={'tema__codigo': 'TEMA_VARIEDAD_CACAO'},
                help_text='Variedad de cacao del lote (temporal)'
            ),
        ),
        migrations.AddField(
            model_name='lote',
            name='estado_fk',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='lotes_temp_estado',
                to='catalogos.parametro',
                limit_choices_to={'tema__codigo': 'TEMA_ESTADO_LOTE'},
                help_text='Estado actual del lote (temporal)'
            ),
        ),
        # Migrate data
        migrations.RunPython(
            normalize_lote_data,
            reverse_normalize_lote_data,
        ),
        # Remove old CharField columns
        migrations.RemoveField(
            model_name='lote',
            name='variedad',
        ),
        migrations.RemoveField(
            model_name='lote',
            name='estado',
        ),
        # Rename temporary ForeignKey columns to final names
        migrations.RenameField(
            model_name='lote',
            old_name='variedad_fk',
            new_name='variedad',
        ),
        migrations.RenameField(
            model_name='lote',
            old_name='estado_fk',
            new_name='estado',
        ),
        # Update related_name and make variedad NOT NULL
        migrations.AlterField(
            model_name='lote',
            name='variedad',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='lotes',
                to='catalogos.parametro',
                limit_choices_to={'tema__codigo': 'TEMA_VARIEDAD_CACAO'},
                help_text='Variedad de cacao del lote'
            ),
        ),
        migrations.AlterField(
            model_name='lote',
            name='estado',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='lotes',
                to='catalogos.parametro',
                limit_choices_to={'tema__codigo': 'TEMA_ESTADO_LOTE'},
                help_text='Estado actual del lote'
            ),
        ),
    ]

