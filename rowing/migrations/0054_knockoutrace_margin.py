# Generated by Django 2.0.6 on 2018-07-09 22:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rowing', '0053_auto_20180709_2258'),
    ]

    operations = [
        migrations.AddField(
            model_name='knockoutrace',
            name='margin',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
