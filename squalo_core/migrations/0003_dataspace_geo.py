# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('squalo_core', '0002_auto_20141224_1839'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataspace',
            name='geo',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
