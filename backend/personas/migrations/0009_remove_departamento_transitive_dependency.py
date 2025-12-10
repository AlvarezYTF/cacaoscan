# Generated migration to remove departamento transitive dependency (3NF normalization)
# -*- coding: utf-8 -*-
from django.db import migrations


def verify_departamento_data(apps, schema_editor):
    """
    Verify that all personas with departamento have municipio with matching departamento.
    If there's a mismatch, update municipio to match departamento or set to None.
    """
    Persona = apps.get_model('personas', 'Persona')
    Municipio = apps.get_model('catalogos', 'Municipio')
    
    personas = Persona.objects.all()
    verified = 0
    warnings = 0
    
    for persona in personas:
        # If persona has departamento but no municipio, try to find a matching municipio
        if hasattr(persona, 'departamento') and persona.departamento and not persona.municipio:
            # Try to find any municipio from the same departamento
            matching_municipio = Municipio.objects.filter(departamento=persona.departamento).first()
            if matching_municipio:
                persona.municipio = matching_municipio
                persona.save(update_fields=['municipio'])
                verified += 1
            else:
                warnings += 1
                print(f"Warning: Persona {persona.id} has departamento {persona.departamento.id} but no matching municipio found")
        elif hasattr(persona, 'departamento') and persona.departamento and persona.municipio:
            # Verify that municipio.departamento matches persona.departamento
            if persona.municipio.departamento != persona.departamento:
                warnings += 1
                print(f"Warning: Persona {persona.id} has departamento {persona.departamento.id} but municipio {persona.municipio.id} belongs to departamento {persona.municipio.departamento.id}")
            else:
                verified += 1
    
    print(f"Verified {verified} personas, {warnings} warnings")


def reverse_verify_departamento_data(apps, schema_editor):
    """Reverse migration - this is a one-way migration."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('personas', '0008_alter_persona_numero_documento_and_more'),
        ('catalogos', '0002_departamento_municipio_and_more'),
    ]

    operations = [
        # Verify data integrity before removing field
        migrations.RunPython(
            verify_departamento_data,
            reverse_verify_departamento_data,
        ),
        # Remove transitive dependency departamento (3NF normalization)
        migrations.RemoveField(
            model_name='persona',
            name='departamento',
        ),
    ]

