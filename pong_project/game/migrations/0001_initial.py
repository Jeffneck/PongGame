# Generated by Django 4.2.18 on 2025-02-05 13:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import game.models
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
                ('tournament_id', models.UUIDField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default='waiting', max_length=10)),
                ('is_online', models.BooleanField(default=False)),
                ('player_left_local', models.CharField(blank=True, max_length=50, null=True)),
                ('player_right_local', models.CharField(blank=True, max_length=50, null=True)),
                ('ready_left', models.BooleanField(default=False)),
                ('ready_right', models.BooleanField(default=False)),
                ('player_left', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='game_sessions_as_player_left', to=settings.AUTH_USER_MODEL)),
                ('player_right', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='game_sessions_as_player_right', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='LocalTournament',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(default='Local Tournament', max_length=100)),
                ('player1', models.CharField(default='mbappe', max_length=50)),
                ('player2', models.CharField(default='zizou', max_length=50)),
                ('player3', models.CharField(default='ribery', max_length=50)),
                ('player4', models.CharField(default='cantona', max_length=50)),
                ('winner_semifinal_1', models.CharField(blank=True, max_length=50, null=True)),
                ('winner_semifinal_2', models.CharField(blank=True, max_length=50, null=True)),
                ('winner_final', models.CharField(blank=True, max_length=50, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default='pending', help_text="Ex: 'pending', 'semifinal1_in_progress', 'semifinal2_in_progress', 'final_in_progress', 'finished', etc.", max_length=30)),
                ('final', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tournament_final', to='game.gamesession')),
                ('semifinal1', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tournament_semifinal1', to='game.gamesession')),
                ('semifinal2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tournament_semifinal2', to='game.gamesession')),
            ],
        ),
        migrations.CreateModel(
            name='TournamentParameters',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ball_speed', models.PositiveSmallIntegerField(choices=[(1, 'Slow'), (2, 'Medium'), (3, 'Fast')], default=2)),
                ('paddle_size', models.PositiveSmallIntegerField(choices=[(1, 'Small'), (2, 'Medium'), (3, 'Large')], default=2)),
                ('bonus_enabled', models.BooleanField(default=True)),
                ('obstacles_enabled', models.BooleanField(default=False)),
                ('tournament', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='parameters', to='game.localtournament')),
            ],
        ),
        migrations.CreateModel(
            name='GameResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('winner_local', models.CharField(blank=True, max_length=50, null=True)),
                ('looser_local', models.CharField(blank=True, max_length=50, null=True)),
                ('score_left', models.IntegerField()),
                ('score_right', models.IntegerField()),
                ('ended_at', models.DateTimeField(auto_now_add=True)),
                ('game', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='game.gamesession')),
                ('looser', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='games_lost', to=settings.AUTH_USER_MODEL)),
                ('winner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='games_won', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='GameParameters',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ball_speed', models.PositiveSmallIntegerField(choices=[(1, 'Slow'), (2, 'Medium'), (3, 'Fast')], default=2)),
                ('paddle_size', models.PositiveSmallIntegerField(choices=[(1, 'Small'), (2, 'Medium'), (3, 'Large')], default=2)),
                ('bonus_enabled', models.BooleanField(default=True)),
                ('obstacles_enabled', models.BooleanField(default=False)),
                ('game_session', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='parameters', to='game.gamesession')),
            ],
        ),
        migrations.CreateModel(
            name='GameInvitation',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField(default=game.models.default_expiration_time)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected'), ('expired', 'Expired')], default='pending', max_length=10)),
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invitations_sent', to=settings.AUTH_USER_MODEL)),
                ('session', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invitations', to='game.gamesession')),
                ('to_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invitations_received', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
