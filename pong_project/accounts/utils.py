# accounts/utils.py

from datetime import timedelta
import jwt
from django.conf import settings
from django.utils import timezone
from .models import RefreshToken


def generate_jwt_token(user, include_refresh=True):
    """
    Génère un Access Token et, si demandé, un Refresh Token pour l'utilisateur.
    
    :param user: Instance de l'utilisateur.
    :param include_refresh: Booléen pour indiquer si le Refresh Token doit être généré.
    :return: Un dictionnaire contenant l'access token, et éventuellement le refresh token.
    """
    current_time = timezone.now()  # Utilise timezone.now() pour un datetime avec fuseau horaire

    # Génère le payload de l'Access Token
    access_payload = {
        'user_id': user.id,
        'username': user.username,
        'exp': current_time + timedelta(hours=1), 
    }
    access_token = jwt.encode(access_payload, settings.SECRET_KEY, algorithm='HS256')

    # Si include_refresh est True, génère également un Refresh Token
    if include_refresh:
        refresh_payload = {
            'user_id': user.id,
            'username': user.username,
            'exp': current_time + timedelta(days=7),  # Durée longue pour le Refresh Token
        }
        refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm='HS256')

        # Stocker le Refresh Token dans la base de données
        RefreshToken.objects.create(
            user=user,
            token=refresh_token,
            expires_at=current_time + timedelta(days=7)  # Utilise un datetime avec fuseau horaire
        )

        return {
            'access_token': access_token.decode('utf-8') if isinstance(access_token, bytes) else access_token,
            'refresh_token': refresh_token.decode('utf-8') if isinstance(refresh_token, bytes) else refresh_token,
        }

    # Retourne uniquement l'Access Token si include_refresh est False
    return {
        'access_token': access_token.decode('utf-8') if isinstance(access_token, bytes) else access_token,
    }
