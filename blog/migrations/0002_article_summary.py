# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-02-18 23:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='summary',
            field=models.CharField(default='default', max_length=1000),
            preserve_default=False,
        ),
    ]