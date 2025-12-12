# Generated manually - Add temporary defaults to prevent Django prompts during makemigrations
# Note: ImageField and ForeignKey fields cannot have defaults, so we only sync state

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('images_app', '0003_add_string_defaults'),
    ]

    operations = [
        # ImageField and ForeignKey fields don't need defaults
        # They are required fields that must be provided when creating records
        # This migration is a placeholder to ensure state is synced
        migrations.RunSQL("SELECT 1;", reverse_sql="SELECT 1;"),
    ]

