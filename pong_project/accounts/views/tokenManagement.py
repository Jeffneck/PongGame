import json
import hashlib
import logging
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from datetime import timedelta
from django.views import View
from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from accounts.models import RefreshToken, CustomUser
from accounts.utils import generate_jwt_token
from pong_project.decorators import login_required_json

logger = logging.getLogger(__name__)

@method_decorator(csrf_protect, name='dispatch')
@method_decorator(login_required_json, name='dispatch')
class RefreshJwtView(View):
    """
    Vue pour gérer les requêtes de rafraîchissement du token.
    Valide le refresh token (en comparant son hash) et délivre un nouveau access token.
    """

    def post(self, request):
        try:
            # Récupère le refresh token depuis le formulaire (FormData)
            refresh_token = request.POST.get('refresh_token')
            if not refresh_token:
                logger.warning("Refresh token not provided in request")
                return JsonResponse({'error': 'Refresh token is required'}, status=400)

            # Décodage du refresh token avec validation de la signature
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=['HS256'])
            # Optionnel : ajouter ici la validation d'autres claims (issuer, audience, etc.)

            # Calcul du hash SHA-256 du refresh token fourni
            hashed_token = hashlib.sha256(refresh_token.encode('utf-8')).hexdigest()

            # Vérifie la validité du refresh token dans la base via son hash
            token_obj = RefreshToken.objects.filter(token=hashed_token).first()
            if not token_obj or not token_obj.is_valid():
                logger.warning("Invalid or expired refresh token")
                return JsonResponse({'error': 'Invalid or expired refresh token', 'error_code': 'token-error'}, status=401)

            # Invalider le refresh token après usage pour éviter sa réutilisation
            token_obj.is_blacklisted = True
            token_obj.save()

            # Récupère l'utilisateur depuis le payload
            user_id = payload.get('user_id')
            user = CustomUser.objects.filter(id=user_id).first()
            if not user:
                logger.warning(f"User with ID {user_id} not found")
                return JsonResponse({'error': 'User not found'}, status=404)

            # Génère un nouveau access token (sans générer de nouveau refresh token)
            new_access_token = generate_jwt_token(user, include_refresh=False)['access_token']

            return JsonResponse({'access_token': new_access_token}, status=200)

        except ExpiredSignatureError:
            logger.warning("Refresh token expired")
            return JsonResponse({'error': 'Refresh token expired', 'error_code': 'token-error'}, status=401)
        except InvalidTokenError:
            logger.warning("Invalid refresh token")
            return JsonResponse({'error': 'Invalid refresh token', 'error_code': 'token-error'}, status=401)
        except Exception as e:
            logger.error(f"Unexpected error during token refresh: {str(e)}")
            return JsonResponse({'error': 'An unexpected error occurred'}, status=500)
