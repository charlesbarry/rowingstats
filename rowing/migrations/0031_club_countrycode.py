# Generated by Django 2.0.6 on 2018-07-01 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rowing', '0030_auto_20180624_2001'),
    ]

    operations = [
        migrations.AddField(
            model_name='club',
            name='countrycode',
            field=models.CharField(blank=True, help_text='Used for national crews, provides the nationality code in international races', max_length=3, null=True),
        ),
    ]