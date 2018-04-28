# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-02-20 22:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0007_auto_20180220_2205'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='public',
            field=models.BooleanField(default=False, help_text='If set to True (checked) the Article will be published. Leave unchecked for draft posts'),
        ),
    ]