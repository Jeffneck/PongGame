import secrets
import hashlib
from datetime import timedelta
from pathlib import Path

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.exceptions import ValidationError

class CustomUser(AbstractUser):
    """
    Utilisateur personnalisé avec gestion de la 2FA, d'un avatar et du statut en ligne.
    """
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

    def clean(self):
        """
        Validation customisée :
         - Si la 2FA est activée, le champ totp_secret ne doit pas être vide.
        """
        super().clean()
        if self.is_2fa_enabled and not self.totp_secret:
            raise ValidationError("Le secret TOTP ne peut pas être vide si la 2FA est activée.")

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
    """
    Code 2FA associé à un utilisateur.
    Le code est généré de manière sécurisée et expire après 10 minutes.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def generate_code(cls, user):
        """
        Génère un code 2FA sécurisé à 6 chiffres en utilisant le module secrets,
        supprime les anciens codes de l'utilisateur et crée un nouvel enregistrement.
        """
        cls.objects.filter(user=user).delete()
        code = ''.join(str(secrets.randbelow(10)) for _ in range(6))
        return cls.objects.create(user=user, code=code)

    def is_valid(self):
        """
        Vérifie si le code est encore valide (expiration après 10 minutes).
        Utilise timezone.now() pour assurer la cohérence des fuseaux horaires.
        """
        return timezone.now() - timedelta(minutes=10) <= self.created_at

    def __str__(self):
        return f"TwoFactorCode(user={self.user}, code={self.code})"


class RefreshToken(models.Model):
    """
    Stocke le refresh token d'un utilisateur.
    Pour augmenter la sécurité, le token est stocké sous forme de hash SHA-256.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='refresh_tokens'
    )
    # Stockage du hash SHA-256 (hex digest de 64 caractères) du token
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_blacklisted = models.BooleanField(default=False)

    def set_token(self, raw_token):
        """
        Calcule et stocke le hash SHA-256 du token brut.
        """
        self.token = hashlib.sha256(raw_token.encode('utf-8')).hexdigest()

    def check_token(self, raw_token):
        """
        Vérifie si le token brut correspond au hash stocké.
        """
        return self.token == hashlib.sha256(raw_token.encode('utf-8')).hexdigest()

    def is_expired(self):
        """Vérifie si le token a expiré."""
        return timezone.now() > self.expires_at

    def is_valid(self):
        """Le token est valide s'il n'est pas expiré et n'est pas blacklisté."""
        return not self.is_expired() and not self.is_blacklisted

    def __str__(self):
        return f"RefreshToken(user={self.user}, expires_at={self.expires_at})"
