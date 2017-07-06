# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-07 23:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('rowing', '0013_auto_20170508_0022'),
    ]

    operations = [
        migrations.RenameField(
            model_name='result',
            old_name='entries',
            new_name='clubs',
        ),
        migrations.AddField(
            model_name='club',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Created on'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='club',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, verbose_name='Last updated'),
        ),
        migrations.AddField(
            model_name='result',
            name='flag',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
