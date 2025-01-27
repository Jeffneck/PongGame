# User/models.py
# ---- Imports standard ----
import random
from datetime import datetime, timedelta
from pathlib import Path

# ---- Imports tiers ----
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.timezone import now


#[DOCUMENTATION] <Django - User & Abstract User>

class CustomUser(AbstractUser):
    """Utilisateur personnalisé."""
    is_2fa_enabled = models.BooleanField(default=False)
    totp_secret = models.CharField(max_length=32, null=True, blank=True)
    friends = models.ManyToManyField('self', symmetrical=True, blank=True)
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        default='avatars/default_avatar.png'
    )
    is_online = models.BooleanField(default=False)

    def match_history(self):
        """Retourne l'historique des parties jouées par l'utilisateur."""
        return GameResult.objects.filter(
            models.Q(player1=self) | models.Q(player2=self)
        ).order_by('-date')

    def __str__(self):
        return self.username




class FriendRequest(models.Model):
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='friend_requests_sent',
        on_delete=models.CASCADE
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='friend_requests_received',
        on_delete=models.CASCADE
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')],
        default='pending'
    )

    def __str__(self):
        return f"{self.from_user} to {self.to_user} - {self.status}"


class TwoFactorCode(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def generate_code(cls, user):
        # Supprimer les anciens codes
        cls.objects.filter(user=user).delete()
        # Générer un nouveau code
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        return cls.objects.create(user=user, code=code)

    def is_valid(self):
        # Le code expire après 10 minutes
        return datetime.now() - timedelta(minutes=10) <= self.created_at.replace(tzinfo=None)


# Stocker les refresh tokens en base de donnee 
# pour pouvoir les comparer a ceux que l' utilisateur nous envoie
# la validite des access tokens est elle geree par PyJWT
class RefreshToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='refresh_tokens')
    token = models.CharField(max_length=255, unique=True)  # Le token JWT
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_blacklisted = models.BooleanField(default=False)  # Permet de marquer un token comme blacklisté (déconnecté) avoir si utile


    def is_expired(self):
        """Vérifie si le token a expiré"""
        return now() > self.expires_at
    
    def is_valid(self):
        return not self.is_expired() and not self.is_blacklisted

    def __str__(self):
        return f"RefreshToken(user={self.user}, expires_at={self.expires_at})"