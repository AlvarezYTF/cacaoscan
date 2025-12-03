# Generated manually for optimization

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_add_model_metrics'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='finca',
            index=models.Index(fields=['agricultor_id'], name='api_finca_agricultor_id_idx'),
        ),
    ]



