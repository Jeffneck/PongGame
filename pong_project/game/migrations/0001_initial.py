# Generated by Django 4.2 on 2025-01-22 20:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GameSession',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('player_left', models.CharField(blank=True, max_length=50, null=True)),
                ('player_right', models.CharField(blank=True, max_length=50, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default='waiting', max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='TournamentParameters',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ball_speed', models.PositiveSmallIntegerField(choices=[(1, 'Slow'), (2, 'Medium'), (3, 'Fast')], default=2)),
                ('racket_size', models.PositiveSmallIntegerField(choices=[(1, 'Small'), (2, 'Medium'), (3, 'Large')], default=2)),
                ('bonus_malus_activation', models.BooleanField(default=True)),
                ('bumpers_activation', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='LocalTournament',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(default='Local Tournament', max_length=100)),
                ('player1', models.CharField(max_length=50)),
                ('player2', models.CharField(max_length=50)),
                ('player3', models.CharField(max_length=50)),
                ('player4', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default='pending', help_text="Status du tournoi: 'pending', 'in_progress', 'finished', etc.", max_length=20)),
                ('final', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tournament_final', to='game.gamesession')),
                ('parameters', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='game.tournamentparameters')),
                ('semifinal1', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tournament_semifinal1', to='game.gamesession')),
                ('semifinal2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tournament_semifinal2', to='game.gamesession')),
            ],
        ),
        migrations.CreateModel(
            name='GameResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('winner', models.CharField(max_length=10)),
                ('looser', models.CharField(max_length=10)),
                ('score_left', models.IntegerField()),
                ('score_right', models.IntegerField()),
                ('ended_at', models.DateTimeField(auto_now_add=True)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.gamesession')),
            ],
        ),
        migrations.CreateModel(
            name='GameParameters',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ball_speed', models.PositiveSmallIntegerField(choices=[(1, 'Slow'), (2, 'Medium'), (3, 'Fast')], default=2)),
                ('racket_size', models.PositiveSmallIntegerField(choices=[(1, 'Small'), (2, 'Medium'), (3, 'Large')], default=2)),
                ('bonus_malus_activation', models.BooleanField(default=True)),
                ('bumpers_activation', models.BooleanField(default=False)),
                ('game_session', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='parameters', to='game.gamesession')),
            ],
        ),
        migrations.CreateModel(
            name='GameInvitation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending', max_length=10)),
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invitations_sent', to=settings.AUTH_USER_MODEL)),
                ('to_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invitations_received', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
