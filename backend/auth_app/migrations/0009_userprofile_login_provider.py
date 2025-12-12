# Generated manually for add_login_provider
# -*- coding: utf-8 -*-

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_app', '0008_emailverification_remove_emailverificationtoken_user_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='login_provider',
            field=models.CharField(
                choices=[('local', 'Local'), ('google', 'Google')],
                default='local',
                help_text='Método de autenticación utilizado por el usuario',
                max_length=20
            ),
        ),
    ]

  