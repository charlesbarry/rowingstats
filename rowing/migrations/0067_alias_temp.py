# Generated by Django 2.1.4 on 2019-07-30 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rowing', '0066_auto_20190729_2329'),
    ]

    operations = [
        migrations.AddField(
            model_name='alias',
            name='temp',
            field=models.BooleanField(default=False),
        ),
    ]
