# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-07-08 16:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rowing', '0024_scoreranking_delta_mu_sigma'),
    ]

    operations = [
        migrations.AddField(
            model_name='scoreranking',
            name='type',
            field=models.CharField(default='Sweep', max_length=10),
        ),
    ]
