# Generated by Django 2.0.6 on 2018-07-05 18:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rowing', '0048_cumlprob_knockout'),
    ]

    operations = [
        migrations.CreateModel(
            name='KnockoutCrews',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('crewname', models.CharField(max_length=100)),
                ('knockout', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rowing.EventInstance')),
            ],
        ),
    ]