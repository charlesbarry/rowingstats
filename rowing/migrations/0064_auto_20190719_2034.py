# Generated by Django 2.1.4 on 2019-07-19 19:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rowing', '0063_auto_20190719_1934'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClubAlias',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=200)),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rowing.Club')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='clubalias',
            unique_together={('club', 'value')},
        ),
    ]