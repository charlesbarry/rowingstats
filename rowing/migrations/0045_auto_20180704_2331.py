# Generated by Django 2.0.6 on 2018-07-04 22:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rowing', '0044_auto_20180704_2329'),
    ]

    operations = [
        migrations.AlterField(
            model_name='result',
            name='clubs',
            field=models.ManyToManyField(blank=True, to='rowing.Club'),
        ),
    ]
