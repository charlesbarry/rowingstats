# Generated by Django 2.0.6 on 2018-07-03 03:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rowing', '0036_auto_20180702_2114'),
    ]

    operations = [
        migrations.CreateModel(
            name='KnockoutRace',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('round', models.PositiveSmallIntegerField(default=0)),
                ('slot', models.PositiveSmallIntegerField(default=0)),
                ('selected', models.BooleanField(default=False)),
                ('child', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='child', to='rowing.Race')),
                ('parent_b', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='parent_b', to='rowing.Race')),
                ('parent_t', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='parent_t', to='rowing.Race')),
                ('race', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rowing.Race')),
            ],
        ),
    ]
