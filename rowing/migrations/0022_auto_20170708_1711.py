# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-07-08 16:11
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rowing', '0021_race_order'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScoreRanking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mu', models.FloatField(default=100.0)),
                ('sigma', models.FloatField(default=10)),
                ('date', models.DateField(verbose_name='Score date')),
                ('rower', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rowing.Rower')),
            ],
        ),
        migrations.AlterField(
            model_name='race',
            name='order',
            field=models.PositiveSmallIntegerField(choices=[('TT/Heat/Single race', 0), ('Semi-Final', 1), ('Final', 2)], default=0),
        ),
        migrations.AlterField(
            model_name='score',
            name='sigma',
            field=models.FloatField(default=10),
        ),
    ]
