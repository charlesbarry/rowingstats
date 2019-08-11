# Generated by Django 2.0.6 on 2018-07-03 04:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rowing', '0038_auto_20180703_0441'),
    ]

    operations = [
        migrations.AlterField(
            model_name='knockoutrace',
            name='child',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='rchild', to='rowing.KnockoutRace'),
        ),
        migrations.AlterField(
            model_name='knockoutrace',
            name='parent_b',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='rparent_b', to='rowing.KnockoutRace'),
        ),
        migrations.AlterField(
            model_name='knockoutrace',
            name='parent_t',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='rparent_t', to='rowing.KnockoutRace'),
        ),
    ]
