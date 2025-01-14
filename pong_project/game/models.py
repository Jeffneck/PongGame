import uuid
from django.db import models

class GameSession(models.Model):
    """
    Un enregistrement pour représenter une partie (en cours ou terminée).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    player_left = models.CharField(max_length=50, null=True, blank=True)
    player_right = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # ex: "running", "finished"
    status = models.CharField(max_length=10, default='running')

    def __str__(self):
        return f"GameSession {self.id} (status={self.status})"

class GameResult(models.Model):
    """
    Enregistre le score final d'une partie terminée.
    """
    game = models.ForeignKey(GameSession, on_delete=models.CASCADE)
    winner = models.CharField(max_length=10)  # "left" ou "right"
    score_left = models.IntegerField()
    score_right = models.IntegerField()
    ended_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.game.id}] winner={self.winner} => {self.score_left}-{self.score_right}"
