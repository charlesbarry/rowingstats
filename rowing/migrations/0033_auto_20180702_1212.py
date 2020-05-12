# Generated by Django 2.0.6 on 2018-07-02 11:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rowing', '0032_auto_20180702_1145'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='cox',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cox', to='rowing.Rower'),
        ),
        migrations.AlterField(
            model_name='event',
            name='type',
            field=models.CharField(choices=[('Sweep', 'Sweep'), ('Sculling', 'Sculling'), ('Lwt Sweep', 'Lightweight Sweep'), ('Lwt Scull', 'Lightweight Sculling'), ('Para-Sweep', 'Para-Sweep'), ('Para-Sculling', 'Para-Sculling')], default='Sweep', max_length=20),
        ),
    ]