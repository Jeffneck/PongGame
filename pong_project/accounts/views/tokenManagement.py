import json
from django.views import View
from django.http import JsonResponse
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from django.conf import settings
from datetime import timedelta
from django.utils.timezone import now
from accounts.models import RefreshToken, CustomUser  # Assurez-vous que CustomUser est importé
import jwt
import logging
from accounts.utils import generate_jwt_token

logger = logging.getLogger(__name__)

class RefreshJwtView(View):
    """
    Class-Based View to handle token refresh requests.
    Validates the refresh token and issues a new access token.
    """

    def post(self, request):
        try:
            # Récupère le refresh token depuis le body JSON
            body = json.loads(request.body)
            refresh_token = body.get('refresh_token')

            if not refresh_token:
                logger.warning("Refresh token not provided in request")
                return JsonResponse({'error': 'Refresh token is required'}, status=400)

            # Décodage du refresh token
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=['HS256'])

            # Vérifie la validité du refresh token dans la base de données
            token_obj = RefreshToken.objects.filter(token=refresh_token).first()
            if not token_obj or not token_obj.is_valid():
                logger.warning("Invalid or expired refresh token")
                return JsonResponse({'error': 'Invalid or expired refresh token'}, status=401)

            # Récupère l'utilisateur à partir du user_id dans le payload
            user_id = payload.get('user_id')
            user = CustomUser.objects.filter(id=user_id).first()
            if not user:
                logger.warning(f"Utilisateur avec ID {user_id} introuvable")
                return JsonResponse({'error': 'User not found'}, status=404)

            # Génère un nouveau access token
            new_access_token = generate_jwt_token(user, include_refresh=False)['access_token']

            return JsonResponse({'access_token': new_access_token}, status=200)

        except ExpiredSignatureError:
            logger.warning("Refresh token expired")
            return JsonResponse({'error': 'Refresh token expired'}, status=401)
        except InvalidTokenError:
            logger.warning("Invalid refresh token")
            return JsonResponse({'error': 'Invalid refresh token'}, status=401)
        except Exception as e:
            logger.error(f"Unexpected error during token refresh: {str(e)}")
            return JsonResponse({'error': 'An unexpected error occurred'}, status=500)
