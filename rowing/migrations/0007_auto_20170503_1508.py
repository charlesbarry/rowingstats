# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-03 14:08
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rowing', '0006_auto_20170502_1029'),
    ]

    operations = [
        migrations.RenameField(
            model_name='race',
            old_name='r_date',
            new_name='date',
        ),
        migrations.RenameField(
            model_name='race',
            old_name='r_class',
            new_name='raceclass',
        ),
        migrations.RenameField(
            model_name='race',
            old_name='r_type',
            new_name='type',
        ),
    ]
