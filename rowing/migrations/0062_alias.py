# Generated by Django 2.1.4 on 2019-07-18 23:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rowing', '0061_race_rnumber'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alias',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=200)),
                ('rower', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rowing.Rower')),
            ],
        ),
    ]