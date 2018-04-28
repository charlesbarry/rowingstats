# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-02-18 16:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=250)),
                ('content', models.TextField()),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name='Last updated')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created on')),
                ('published', models.DateTimeField(verbose_name='Published on')),
            ],
        ),
    ]