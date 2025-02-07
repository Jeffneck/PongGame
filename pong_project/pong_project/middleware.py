import logging
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from accounts.models import CustomUser
import jwt

logger = logging.getLogger(__name__)

class JWTAuthenticationMiddleware:
    """
    Middleware d'authentification JWT.
    
    Extrait et décode le token JWT présent dans le header Authorization.
    En cas d'erreur ou d'absence de token, request.user est défini sur AnonymousUser.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()  # Extrait le token après "Bearer "
            try:
                # Décode le token JWT en utilisant la clé secrète et l'algorithme HS256
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                user_id = payload.get('user_id')
                if not user_id:
                    raise jwt.InvalidTokenError("Le payload ne contient pas d'ID utilisateur")
                
                try:
                    user = CustomUser.objects.get(id=user_id)
                except CustomUser.DoesNotExist:
                    logger.debug("Utilisateur introuvable pour l'ID : %s", user_id)
                    user = AnonymousUser()
                request.user = user

            except jwt.ExpiredSignatureError:
                logger.warning("Le jeton JWT a expiré.")
                request.user = AnonymousUser()
            except jwt.InvalidTokenError as e:
                logger.warning("Jeton JWT invalide : %s", e)
                request.user = AnonymousUser()
            except Exception as e:
                logger.error("Erreur inattendue lors de l'authentification JWT : %s", e)
                request.user = AnonymousUser()
        else:
            logger.debug("Aucun jeton JWT fourni ou format invalide dans le header Authorization.")
            request.user = AnonymousUser()

        response = self.get_response(request)
        return response
