# from django.db import models

# class GameResult(models.Model):
#     winner = models.CharField(max_length=10)  # "left" ou "right"
#     score_left = models.IntegerField()
#     score_right = models.IntegerField()
#     played_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Winner: {self.winner} - {self.score_left} vs {self.score_right} ({self.played_at})"


# game/models.py
import uuid
from django.db import models

class GameSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    player_left = models.CharField(max_length=50, blank=True, null=True)
    player_right = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # ... tu peux ajouter un status ("running", "finished"), etc.

    def __str__(self):
        return f"Game {self.id} (left={self.player_left}, right={self.player_right})"