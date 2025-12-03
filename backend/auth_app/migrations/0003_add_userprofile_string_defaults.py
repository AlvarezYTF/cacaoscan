# Generated manually - Add default="" to all nullable string fields in UserProfile
# This prevents Django from asking for one-off defaults when changing null=True to null=False

from django.db import migrations, models


def set_default_string_fields(apps, schema_editor):
    """Set empty string for null values in string fields."""
    UserProfile = apps.get_model('auth_app', 'UserProfile')
    
    # Update all nullable string fields to empty string
    UserProfile.objects.filter(phone_number__isnull=True).update(phone_number="")
    UserProfile.objects.filter(region__isnull=True).update(region="")
    UserProfile.objects.filter(municipality__isnull=True).update(municipality="")
    UserProfile.objects.filter(farm_name__isnull=True).update(farm_name="")


def reverse_set_default_string_fields(apps, schema_editor):
    """Reverse migration - set null back."""
    UserProfile = apps.get_model('auth_app', 'UserProfile')
    
    # Reverse: set empty strings back to null
    UserProfile.objects.filter(phone_number="").update(phone_number=None)
    UserProfile.objects.filter(region="").update(region=None)
    UserProfile.objects.filter(municipality="").update(municipality=None)
    UserProfile.objects.filter(farm_name="").update(farm_name=None)


class Migration(migrations.Migration):

    dependencies = [
        ('auth_app', '0002_pendingemailverification'),
    ]

    operations = [
        # First, set default values for existing null records
        migrations.RunPython(
            set_default_string_fields,
            reverse_set_default_string_fields
        ),
        # Then, alter all fields to add default="" and remove null=True
        migrations.AlterField(
            model_name='userprofile',
            name='phone_number',
            field=models.CharField(
                blank=True,
                default="",
                max_length=20
            ),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='region',
            field=models.CharField(
                blank=True,
                default="",
                max_length=100
            ),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='municipality',
            field=models.CharField(
                blank=True,
                default="",
                max_length=100
            ),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='farm_name',
            field=models.CharField(
                blank=True,
                default="",
                max_length=200
            ),
        ),
    ]

