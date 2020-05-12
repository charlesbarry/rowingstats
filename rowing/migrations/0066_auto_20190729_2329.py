# Generated by Django 2.1.4 on 2019-07-29 22:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rowing', '0065_club_country'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='alias',
            options={'verbose_name_plural': 'aliases'},
        ),
        migrations.AlterModelOptions(
            name='clubalias',
            options={'verbose_name_plural': 'clubAliases'},
        ),
        migrations.AlterUniqueTogether(
            name='time',
            unique_together={('result', 'description')},
        ),
    ]