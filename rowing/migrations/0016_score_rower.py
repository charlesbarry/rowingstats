# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-08 00:14
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rowing', '0015_auto_20170508_0110'),
    ]

    operations = [
        migrations.AddField(
            model_name='score',
            name='rower',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='rowing.Rower'),
            preserve_default=False,
        ),
    ]
