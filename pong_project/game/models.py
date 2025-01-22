import uuid
from django.db import models
from django.conf import settings

class GameSession(models.Model):
    """
    Un enregistrement pour représenter une partie (en cours ou terminée).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    player_left = models.CharField(max_length=50, null=True, blank=True)
    player_right = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # ex: "waiting", "running", "finished"
    status = models.CharField(max_length=10, default='waiting')

    def __str__(self):
        return f"GameSession {self.id} (status={self.status})"


class GameParameters(models.Model):
    game_session = models.OneToOneField(GameSession, related_name='parameters', on_delete=models.CASCADE)
    BALL_SPEED_CHOICES = [(1, 'Slow'), (2, 'Medium'), (3, 'Fast'),]
    ball_speed = models.PositiveSmallIntegerField(choices=BALL_SPEED_CHOICES, default=2)

    RACKET_SIZE_CHOICES = [(1, 'Small'), (2, 'Medium'), (3, 'Large'),]
    racket_size = models.PositiveSmallIntegerField(choices=RACKET_SIZE_CHOICES, default=2)

    bonus_malus_activation = models.BooleanField(default=True)
    bumpers_activation = models.BooleanField(default=False)


    def __str__(self):
        return (f"Ball speed: {self.get_ball_speed_display()}, "
                f"Racket size: {self.get_racket_size_display()}, "
                f"Bonus/Malus: {'On' if self.bonus_malus_activation else 'Off'}, "
                f"Bumpers: {'On' if self.bumpers_activation else 'Off'}")

#remplacer game par game_session
class GameResult(models.Model):
    """
    Enregistre le score final d'une partie terminée.
    """
    game = models.ForeignKey(GameSession, on_delete=models.CASCADE)
    winner = models.CharField(max_length=10)  # "left" ou "right"
    looser = models.CharField(max_length=10)  # "left" ou "right"
    score_left = models.IntegerField()
    score_right = models.IntegerField()
    ended_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.game.id}] winner={self.winner} looser={self.looser} => {self.score_left}-{self.score_right}"



class GameInvitation(models.Model):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='invitations_sent', on_delete=models.CASCADE)
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='invitations_received', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')],
        default='pending'
    )
    
    def __str__(self):
        return f"Invitation de {self.from_user.username} à {self.to_user.username} - {self.status}"
    
# TOURNAMENT MODELS

class TournamentParameters(models.Model):
    BALL_SPEED_CHOICES = [(1, 'Slow'), (2, 'Medium'), (3, 'Fast')]
    ball_speed = models.PositiveSmallIntegerField(choices=BALL_SPEED_CHOICES, default=2)

    RACKET_SIZE_CHOICES = [(1, 'Small'), (2, 'Medium'), (3, 'Large')]
    racket_size = models.PositiveSmallIntegerField(choices=RACKET_SIZE_CHOICES, default=2)

    bonus_malus_activation = models.BooleanField(default=True)
    bumpers_activation = models.BooleanField(default=False)

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
        max_length=20,
        default='pending',  
        help_text="Status du tournoi: 'pending', 'in_progress', 'finished', etc."
    )

    def __str__(self):
        return f"Tournament {self.name} - {self.id}"