# game/models.py
from django.db import models
from accounts.models import CustomUser
from django.utils.timezone import now
from datetime import timedelta
import uuid



class GameSession(models.Model):
    """
    Un enregistrement pour représenter une partie (en cours ou terminée).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tournament_id = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, default='waiting')
    
    # Le champ is_online pour déterminer si c'est une partie en ligne ou locale
    is_online = models.BooleanField(default=False)

    # Si la partie est en ligne, on relie à un CustomUser
    player_left = models.ForeignKey(CustomUser, related_name='game_sessions_as_player_left', on_delete=models.CASCADE, null=True, blank=True)
    player_right = models.ForeignKey(CustomUser, related_name='game_sessions_as_player_right', on_delete=models.CASCADE, null=True, blank=True)

    # Si la partie est locale, on utilise des champs de texte (par exemple, les noms des joueurs)
    player_left_name = models.CharField(max_length=50, null=True, blank=True)
    player_right_name = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"GameSession {self.id} (status={self.status})"




class GameParameters(models.Model):
    game_session = models.OneToOneField(GameSession, related_name='parameters', on_delete=models.CASCADE)
    BALL_SPEED_CHOICES = [(1, 'Slow'), (2, 'Medium'), (3, 'Fast'),]
    ball_speed = models.PositiveSmallIntegerField(choices=BALL_SPEED_CHOICES, default=2)

    paddle_size_CHOICES = [(1, 'Small'), (2, 'Medium'), (3, 'Large'),]
    paddle_size = models.PositiveSmallIntegerField(choices=paddle_size_CHOICES, default=2)

    bonus_enabled = models.BooleanField(default=True)
    obstacles_enabled = models.BooleanField(default=False)


    def __str__(self):
        return (f"Ball speed: {self.get_ball_speed_display()}, "
                f"paddle size: {self.get_paddle_size_display()}, "
                f"Bonus/Malus: {'On' if self.bonus_enabled else 'Off'}, "
                f"Bumpers: {'On' if self.obstacles_enabled else 'Off'}")

#remplacer game par game_session
class GameResult(models.Model):
    """
    Enregistre le score final d'une partie terminée.
    """
    game = models.ForeignKey(GameSession, on_delete=models.CASCADE)
    winner = models.CharField(max_length=50)  # "left" ou "right"
    looser = models.CharField(max_length=50)  # "left" ou "right"
    score_left = models.IntegerField()
    score_right = models.IntegerField()
    ended_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.game.id}] winner={self.winner} looser={self.looser} => {self.score_left}-{self.score_right}"



# TOURNAMENT MODELS

class TournamentParameters(models.Model):
    BALL_SPEED_CHOICES = [(1, 'Slow'), (2, 'Medium'), (3, 'Fast')]
    ball_speed = models.PositiveSmallIntegerField(choices=BALL_SPEED_CHOICES, default=2)

    paddle_size_CHOICES = [(1, 'Small'), (2, 'Medium'), (3, 'Large')]
    paddle_size = models.PositiveSmallIntegerField(choices=paddle_size_CHOICES, default=2)

    bonus_enabled = models.BooleanField(default=True)
    obstacles_enabled = models.BooleanField(default=False)

class LocalTournament(models.Model):
    """
    Modèle pour gérer un tournoi local à 4 joueurs (type 'mini-bracket').
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, default='Local Tournament')
    # Les pseudos ou Users pour les 4 joueurs
    player1 = models.CharField(max_length=50)
    player2 = models.CharField(max_length=50)
    player3 = models.CharField(max_length=50)
    player4 = models.CharField(max_length=50)
    

    # Parties du bracket : 2 demi-finales + 1 finale
    semifinal1 = models.ForeignKey(
        'GameSession',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='tournament_semifinal1'
    )
    semifinal2 = models.ForeignKey(
        'GameSession',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='tournament_semifinal2'
    )
    final = models.ForeignKey(
        'GameSession',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='tournament_final'
    )

    # Paramètres de jeu (pour dupliquer sur chaque partie)
    # On met un on_delete = SET_NULL (ou CASCADE si tu préfères)
    parameters = models.OneToOneField(
        TournamentParameters,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=30,
        default='pending',  
        help_text="Status du tournoi: 'pending', ''semifinal1_in_progress', 'semifinal2_in_progress', 'final_in_progress', 'finished', etc."
    )

    def __str__(self):
        return f"Tournament {self.name} - {self.id}"



# INVITATIONS ----------------------------------------


# utile pour savoir si une invitation a expire
def default_expiration_time():
    """Retourne l'heure actuelle + 5 minutes."""
    return now() + timedelta(minutes=5)

class GameInvitation(models.Model):
    from_user = models.ForeignKey(CustomUser, related_name='invitations_sent', on_delete=models.CASCADE)
    to_user = models.ForeignKey(CustomUser, related_name='invitations_received', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=default_expiration_time)
    status = models.CharField(
        max_length=10,
        choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected'), ('expired', 'Expired')],
        default='pending',
    )
    # NOUVEAU : permet de relier directement l'invitation à la session créée (si acceptée)
    session = models.ForeignKey(
        'GameSession',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='invitations'
    )

    def is_expired(self):
        return now() > self.expires_at

    def __str__(self):
        if self.status == 'expired':
            return f"Invitation expirée de {self.from_user.username} à {self.to_user.username}"
        return f"Invitation de {self.from_user.username} à {self.to_user.username} - {self.status}"


class GameInvitationParameters(models.Model):
    """
    Permet de stocker les paramètres de jeu pour une invitation en ligne
    (avant que la session ne soit créée).
    """
    invitation = models.OneToOneField(
        GameInvitation,
        on_delete=models.CASCADE,
        related_name='parameters'
    )

    BALL_SPEED_CHOICES = [(1, 'Slow'), (2, 'Medium'), (3, 'Fast')]
    ball_speed = models.PositiveSmallIntegerField(choices=BALL_SPEED_CHOICES, default=2)

    paddle_size_CHOICES = [(1, 'Small'), (2, 'Medium'), (3, 'Large')]
    paddle_size = models.PositiveSmallIntegerField(choices=paddle_size_CHOICES, default=2)

    bonus_enabled = models.BooleanField(default=True)
    obstacles_enabled = models.BooleanField(default=False)

    def __str__(self):
        return (f"(Invitation={self.invitation.id}) "
                f"BallSpeed={self.get_ball_speed_display()}, "
                f"RacketSize={self.get_paddle_size_display()}, "
                f"Bonus={self.bonus_enabled}, Bumpers={self.obstacles_enabled}")