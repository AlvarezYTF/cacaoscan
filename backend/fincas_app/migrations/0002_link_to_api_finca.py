from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('fincas_app', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql='-- Linking Finca model to existing table api_finca; no schema change.',
            reverse_sql='-- Unlink note only; no schema change to reverse.'
        ),
    ]




