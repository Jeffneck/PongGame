# Generated by Django 4.2.18 on 2025-01-31 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='localtournament',
            name='winner_final',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='localtournament',
            name='winner_semifinal_1',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='localtournament',
            name='winner_semifinal_2',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
