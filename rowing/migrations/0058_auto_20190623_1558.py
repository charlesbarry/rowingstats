# Generated by Django 2.2.2 on 2019-06-23 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rowing', '0057_auto_20180715_2234'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rower',
            name='iscox',
        ),
        migrations.AddField(
            model_name='rower',
            name='wrid',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]