# Generated by Django 2.0.6 on 2018-07-07 02:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rowing', '0051_auto_20180705_2357'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventinstance',
            name='complete',
            field=models.BooleanField(default=True),
        ),
    ]