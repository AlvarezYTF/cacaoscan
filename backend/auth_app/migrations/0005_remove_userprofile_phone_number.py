# Generated manually - Remove phone_number from UserProfile
# phone_number is now managed in Persona model (personas.Persona.telefono)
# -*- coding: utf-8 -*-

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth_app', '0004_remove_userprofile_farm_name_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='phone_number',
        ),
    ]


