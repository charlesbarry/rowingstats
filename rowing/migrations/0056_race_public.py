# Generated by Django 2.0.6 on 2018-07-15 21:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rowing', '0055_auto_20180715_2218'),
    ]

    operations = [
        migrations.AddField(
            model_name='race',
            name='public',
            field=models.BooleanField(default=True, help_text='If set to True (checked) the Race will be displayed publicly in results pages.'),
        ),
    ]