# Generated by Django 4.2.19 on 2025-02-07 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gamesession',
            name='status',
            field=models.CharField(choices=[('waiting', 'Waiting'), ('running', 'Running'), ('finished', 'Finished')], default='waiting', max_length=10),
        ),
    ]
