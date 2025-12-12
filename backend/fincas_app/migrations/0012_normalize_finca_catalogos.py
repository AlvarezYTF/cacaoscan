# Generated migration to normalize Finca model with catalogs
# -*- coding: utf-8 -*-
from django.db import migrations, models
import django.db.models.deletion


def normalize_finca_data(apps, schema_editor):
    """Migrate Finca data from CharField to ForeignKeys to Parametro."""
    Finca = apps.get_model('fincas_app', 'Finca')
    Parametro = apps.get_model('catalogos', 'Parametro')
    Tema = apps.get_model('catalogos', 'Tema')
    
    # Get themes
    try:
        tema_tipo_suelo = Tema.objects.get(codigo='TEMA_TIPO_SUELO')
        tema_clima = Tema.objects.get(codigo='TEMA_CLIMA')
        tema_estado_finca = Tema.objects.get(codigo='TEMA_ESTADO_FINCA')
    except Tema.DoesNotExist:
        print("WARNING: Required themes not found. Skipping Finca catalog migration.")
        return
    
    # Mapping functions
    def find_tipo_suelo(value):
        """Find Parametro (TEMA_TIPO_SUELO) by name (case insensitive)."""
        if not value:
            return None
        value_upper = value.upper().strip()
        # Try exact match first
        try:
            return Parametro.objects.get(tema=tema_tipo_suelo, codigo=value_upper)
        except Parametro.DoesNotExist:
            pass
        # Try by name
        try:
            return Parametro.objects.filter(tema=tema_tipo_suelo, nombre__iexact=value).first()
        except:
            pass
        # Default to ARCILLOSO if exists
        return Parametro.objects.filter(tema=tema_tipo_suelo, codigo='ARCILLOSO').first()
    
    def find_clima(value):
        """Find Parametro (TEMA_CLIMA) by name (case insensitive)."""
        if not value:
            return None
        value_upper = value.upper().strip()
        # Try exact match first
        try:
            return Parametro.objects.get(tema=tema_clima, codigo=value_upper)
        except Parametro.DoesNotExist:
            pass
        # Try by name
        try:
            return Parametro.objects.filter(tema=tema_clima, nombre__iexact=value).first()
        except:
            pass
        # Default to TROPICAL if exists
        return Parametro.objects.filter(tema=tema_clima, codigo='TROPICAL').first()
    
    def find_estado_finca(value):
        """Find Parametro (TEMA_ESTADO_FINCA) by name (case insensitive)."""
        if not value:
            return None
        value_upper = value.upper().strip()
        # Map common values
        mapping = {
            'activa': 'ACTIVA',
            'inactiva': 'INACTIVA',
            'suspendida': 'SUSPENDIDA',
        }
        codigo = mapping.get(value_upper, value_upper)
        try:
            return Parametro.objects.get(tema=tema_estado_finca, codigo=codigo)
        except Parametro.DoesNotExist:
            pass
        # Try by name
        try:
            return Parametro.objects.filter(tema=tema_estado_finca, nombre__iexact=value).first()
        except:
            pass
        # Default to ACTIVA if exists
        return Parametro.objects.filter(tema=tema_estado_finca, codigo='ACTIVA').first()
    
    # Migrate data
    fincas = Finca.objects.all()
    migrated_tipo_suelo = 0
    migrated_clima = 0
    migrated_estado = 0
    
    for finca in fincas:
        # Migrate tipo_suelo (from CharField to temporary FK)
        tipo_suelo_value = getattr(finca, 'tipo_suelo', None)
        if tipo_suelo_value and isinstance(tipo_suelo_value, str):
            tipo_suelo_obj = find_tipo_suelo(tipo_suelo_value)
            if tipo_suelo_obj:
                finca.tipo_suelo_fk_id = tipo_suelo_obj.id
                migrated_tipo_suelo += 1
        
        # Migrate clima (from CharField to temporary FK)
        clima_value = getattr(finca, 'clima', None)
        if clima_value and isinstance(clima_value, str):
            clima_obj = find_clima(clima_value)
            if clima_obj:
                finca.clima_fk_id = clima_obj.id
                migrated_clima += 1
        
        # Migrate estado (from CharField to temporary FK)
        estado_value = getattr(finca, 'estado', None)
        if estado_value and isinstance(estado_value, str):
            estado_obj = find_estado_finca(estado_value)
            if estado_obj:
                finca.estado_fk_id = estado_obj.id
                migrated_estado += 1
        
        finca.save(update_fields=['tipo_suelo_fk_id', 'clima_fk_id', 'estado_fk_id'])
    
    print(f"Migrated {migrated_tipo_suelo} tipo_suelo, {migrated_clima} clima, {migrated_estado} estado")


def reverse_normalize_finca_data(apps, schema_editor):
    """Reverse migration - convert ForeignKeys back to CharField."""
    Finca = apps.get_model('fincas_app', 'Finca')
    # This is a one-way migration - we don't reverse it
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('fincas_app', '0011_remove_finca_api_finca_municip_582e68_idx_and_more'),
        ('catalogos', '0013_create_themes_and_migrate_catalogs'),  # Use unified catalog system
    ]

    operations = [
        # Add temporary ForeignKey columns with different names
        migrations.AddField(
            model_name='finca',
            name='tipo_suelo_fk',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='fincas_temp',
                to='catalogos.parametro',
                limit_choices_to={'tema__codigo': 'TEMA_TIPO_SUELO'},
                help_text='Tipo de suelo de la finca (temporal)'
            ),
        ),
        migrations.AddField(
            model_name='finca',
            name='clima_fk',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='fincas_temp_clima',
                to='catalogos.parametro',
                limit_choices_to={'tema__codigo': 'TEMA_CLIMA'},
                help_text='Tipo de clima de la finca (temporal)'
            ),
        ),
        migrations.AddField(
            model_name='finca',
            name='estado_fk',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='fincas_temp_estado',
                to='catalogos.parametro',
                limit_choices_to={'tema__codigo': 'TEMA_ESTADO_FINCA'},
                help_text='Estado de la finca (temporal)'
            ),
        ),
        # Migrate data (using temporary column names)
        migrations.RunPython(
            normalize_finca_data,
            reverse_normalize_finca_data,
        ),
        # Remove old CharField columns
        migrations.RemoveField(
            model_name='finca',
            name='tipo_suelo',
        ),
        migrations.RemoveField(
            model_name='finca',
            name='clima',
        ),
        migrations.RemoveField(
            model_name='finca',
            name='estado',
        ),
        # Rename temporary ForeignKey columns to final names
        migrations.RenameField(
            model_name='finca',
            old_name='tipo_suelo_fk',
            new_name='tipo_suelo',
        ),
        migrations.RenameField(
            model_name='finca',
            old_name='clima_fk',
            new_name='clima',
        ),
        migrations.RenameField(
            model_name='finca',
            old_name='estado_fk',
            new_name='estado',
        ),
        # Update related_name for ForeignKeys
        migrations.AlterField(
            model_name='finca',
            name='tipo_suelo',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='fincas',
                to='catalogos.parametro',
                limit_choices_to={'tema__codigo': 'TEMA_TIPO_SUELO'},
                help_text='Tipo de suelo de la finca'
            ),
        ),
        migrations.AlterField(
            model_name='finca',
            name='clima',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='fincas',
                to='catalogos.parametro',
                limit_choices_to={'tema__codigo': 'TEMA_CLIMA'},
                help_text='Tipo de clima de la finca'
            ),
        ),
        migrations.AlterField(
            model_name='finca',
            name='estado',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='fincas',
                to='catalogos.parametro',
                limit_choices_to={'tema__codigo': 'TEMA_ESTADO_FINCA'},
                help_text='Estado de la finca'
            ),
        ),
        # Add indexes
        migrations.AddIndex(
            model_name='finca',
            index=models.Index(fields=['estado'], name='api_finca_estado_idx'),
        ),
        migrations.AddIndex(
            model_name='finca',
            index=models.Index(fields=['tipo_suelo'], name='api_finca_tipo_suelo_idx'),
        ),
        migrations.AddIndex(
            model_name='finca',
            index=models.Index(fields=['clima'], name='api_finca_clima_idx'),
        ),
    ]

