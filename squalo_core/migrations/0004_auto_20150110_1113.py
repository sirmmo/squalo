# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('squalo_core', '0003_dataspace_geo'),
    ]

    operations = [
        migrations.AddField(
            model_name='field',
            name='geo',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='model',
            name='internal',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
