# Generated manually - Add default="" to failure_reason field
# -*- coding: utf-8 -*-
# This prevents Django from asking for one-off default when adding the field

from django.db import migrations, models


def set_default_failure_reason(apps, schema_editor):
    """Set empty string for null failure_reason values."""
    LoginHistory = apps.get_model('audit', 'LoginHistory')
    LoginHistory.objects.filter(failure_reason__isnull=True).update(failure_reason="")


def reverse_set_default_failure_reason(apps, schema_editor):
    """Reverse migration - set null back."""
    LoginHistory = apps.get_model('audit', 'LoginHistory')
    LoginHistory.objects.filter(failure_reason="").update(failure_reason=None)


class Migration(migrations.Migration):

    dependencies = [
        ('audit', '0002_activitylog'),
    ]

    operations = [
        # First, set default values for existing null records
        migrations.RunPython(
            set_default_failure_reason,
            reverse_set_default_failure_reason
        ),
        # Then, alter the field to add default=""
        migrations.AlterField(
            model_name='loginhistory',
            name='failure_reason',
            field=models.CharField(
                blank=True,
                default="",
                help_text='Razón del fallo si no fue exitoso',
                max_length=200
            ),
        ),
    ]

