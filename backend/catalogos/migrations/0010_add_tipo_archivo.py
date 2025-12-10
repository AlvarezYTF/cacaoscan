# Generated migration to add TipoArchivo catalog (1NF normalization)
# -*- coding: utf-8 -*-
from django.db import migrations, models


def create_default_tipos_archivo(apps, schema_editor):
    """Create default file types."""
    TipoArchivo = apps.get_model('catalogos', 'TipoArchivo')
    
    tipos = [
        ('IMAGE_JPEG', 'JPEG', 'image/jpeg', 'Imagen JPEG'),
        ('IMAGE_JPG', 'JPG', 'image/jpg', 'Imagen JPG'),
        ('IMAGE_PNG', 'PNG', 'image/png', 'Imagen PNG'),
        ('IMAGE_WEBP', 'WebP', 'image/webp', 'Imagen WebP'),
    ]
    
    for codigo, nombre, mime_type, descripcion in tipos:
        TipoArchivo.objects.get_or_create(
            codigo=codigo,
            defaults={
                'nombre': nombre,
                'mime_type': mime_type,
                'descripcion': descripcion,
                'activo': True
            }
        )


def reverse_create_default_tipos_archivo(apps, schema_editor):
    """Reverse migration - delete all tipos."""
    TipoArchivo = apps.get_model('catalogos', 'TipoArchivo')
    TipoArchivo.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('catalogos', '0009_rename_catalogos_t_codigo_8a1b2c_idx_catalogos_t_codigo_62be96_idx_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TipoArchivo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(help_text='Código único del tipo (ej: IMAGE_JPEG, IMAGE_PNG, IMAGE_WEBP)', max_length=50, unique=True)),
                ('nombre', models.CharField(help_text='Nombre del tipo de archivo (ej: JPEG, PNG, WebP)', max_length=100)),
                ('mime_type', models.CharField(help_text='MIME type del archivo (ej: image/jpeg, image/png)', max_length=100)),
                ('descripcion', models.TextField(blank=True, default='', help_text='Descripción del tipo de archivo')),
                ('activo', models.BooleanField(default=True, help_text='Indica si el tipo está activo')),
            ],
            options={
                'verbose_name': 'Tipo de Archivo',
                'verbose_name_plural': 'Tipos de Archivo',
                'ordering': ['nombre'],
            },
        ),
        migrations.AddIndex(
            model_name='tipoarchivo',
            index=models.Index(fields=['codigo'], name='catalogos_t_codigo_archivo_idx'),
        ),
        migrations.AddIndex(
            model_name='tipoarchivo',
            index=models.Index(fields=['mime_type'], name='catalogos_t_mime_type_idx'),
        ),
        migrations.AddIndex(
            model_name='tipoarchivo',
            index=models.Index(fields=['activo'], name='catalogos_t_activo_archivo_idx'),
        ),
        migrations.RunPython(
            create_default_tipos_archivo,
            reverse_create_default_tipos_archivo,
        ),
    ]

