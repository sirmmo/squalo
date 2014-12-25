# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('squalo_core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataspace',
            name='owner',
            field=models.ForeignKey(related_name='dataspaces', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
