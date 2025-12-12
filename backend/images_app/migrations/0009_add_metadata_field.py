# Generated manually - Add metadata field to CacaoImage
# -*- coding: utf-8 -*-

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('images_app', '0008_remove_cacaoimage_images_app__finca_i_850928_idx_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cacaoimage',
            name='metadata',
            field=models.JSONField(blank=True, default=dict, help_text='Metadata adicional en formato JSON'),
        ),
    ]


