# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-07 08:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rowing', '0010_rower_nationality'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rower',
            name='nationality',
            field=models.CharField(default='GBR', max_length=8),
        ),
    ]
