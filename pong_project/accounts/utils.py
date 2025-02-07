import hashlib
from datetime import timedelta
import jwt
from django.conf import settings
from django.utils import timezone
from .models import RefreshToken

def generate_jwt_token(user, include_refresh=True):
    """
    Génère un Access Token et, si demandé, un Refresh Token pour l'utilisateur.
    
    :param user: Instance de l'utilisateur.
    :param include_refresh: Booléen indiquant si le Refresh Token doit être généré.
    :return: Un dictionnaire contenant l'access token, et éventuellement le refresh token.
    """
    current_time = timezone.now()

    # Génère le payload de l'Access Token
    access_payload = {
        'user_id': user.id,
        'username': user.username,
        'exp': current_time + timedelta(hours=1),
    }
    access_token = jwt.encode(access_payload, settings.SECRET_KEY, algorithm='HS256')
    if isinstance(access_token, bytes):
        access_token = access_token.decode('utf-8')

    tokens = {'access_token': access_token}

    if include_refresh:
        # Génère le payload du Refresh Token
        refresh_payload = {
            'user_id': user.id,
            'username': user.username,
            'exp': current_time + timedelta(days=7),
        }
        refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm='HS256')
        if isinstance(refresh_token, bytes):
            refresh_token = refresh_token.decode('utf-8')
        
        refresh_expires_at = current_time + timedelta(days=7)
        
        # Calculer le hash SHA-256 du refresh token
        hashed_token = hashlib.sha256(refresh_token.encode('utf-8')).hexdigest()
        
        # Stocker le Refresh Token dans la base de données (sous forme de hash)
        RefreshToken.objects.create(
            user=user,
            token=hashed_token,
            expires_at=refresh_expires_at
        )

        tokens['refresh_token'] = refresh_token

    return tokens
