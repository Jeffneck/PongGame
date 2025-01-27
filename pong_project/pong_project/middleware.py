import logging
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from accounts.models import CustomUser  # Importe le modèle utilisateur personnalisé
import jwt

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.headers.get('Authorization', None)

        if auth_header:

            #logger.debug(f"Auth_header = : {auth_header}")
            try:
                logger.debug("Validation du jeton JWT")

                # Extrait le jeton
                token = auth_header.split(' ')[1]

                #logger.debug(f"Jeton JWT extrait : {token}")
                
                # Décode le jeton
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                user_id = payload.get('user_id')
                logger.debug(payload)

                if not user_id:
                    raise jwt.DecodeError("Le payload ne contient pas d'ID utilisateur")

                # Récupération de l'utilisateur
                user = CustomUser.objects.filter(id=user_id).first()

                if not user:
                    logger.debug(f"Utilisateur introuvable avec l'ID : {user_id}")
                    request.user = AnonymousUser()
                else:
                    logger.debug(f"Utilisateur authentifié : {user.username}")
                    request.user = user

            except jwt.ExpiredSignatureError:
                logger.warning("Le jeton JWT a expiré")
                request.user = AnonymousUser()
            except jwt.DecodeError:
                logger.warning("Le jeton JWT est invalide")
                request.user = AnonymousUser()
            except Exception as e:
                logger.error(f"Erreur inattendue lors de l'authentification JWT : {str(e)}")
                request.user = AnonymousUser()
        else:
            logger.debug("Aucun jeton JWT fourni")
            request.user = AnonymousUser()

        response = self.get_response(request)
        return response



# __init__(self, get_response)
# Fonctionnement : La méthode __init__ est le constructeur de la classe. Elle est appelée lorsque le middleware est initialisé.
# Explication : get_response est une fonction que Django appelle pour obtenir la réponse finale. Le middleware doit appeler cette fonction à un moment donné pour que le traitement continue. Ici, self.get_response garde cette fonction pour être utilisée plus tard dans __call__.
# 2. __call__(self, request)
# Fonctionnement : La méthode __call__ est appelée pour chaque requête HTTP que le serveur reçoit. Elle permet au middleware d'intercepter la requête avant qu'elle n'atteigne la vue, et aussi de modifier la réponse avant qu'elle ne soit envoyée au client.
# Explication : Ce qui se passe ici, c'est que le middleware vérifie si un token JWT est présent dans les en-têtes de la requête (c'est-à-dire dans le champ Authorization des en-têtes HTTP).
# 3. auth_header = request.headers.get('Authorization', None)
# Fonctionnement : Cette ligne cherche dans les en-têtes de la requête (request.headers) une clé appelée 'Authorization'. Si elle existe, sa valeur sera récupérée dans auth_header, sinon None sera retourné par défaut.
# Explication : Ce champ d'en-tête est où le token JWT est généralement envoyé par le client (par exemple, dans le format Authorization: Bearer <token>).
# 4. Vérification si auth_header existe
# Explication : Si auth_header est présent, cela signifie que la requête contient un token JWT. Le middleware va donc essayer de l'extraire et de le décoder.
# 5. token = auth_header.split(' ')[1]
# Fonctionnement : Cette ligne extrait le token en utilisant split(' '), qui divise le contenu de auth_header en deux parties : la première partie (avant l'espace) est le mot Bearer, et la deuxième partie est le token lui-même. On récupère donc le deuxième élément de la liste avec [1].
# Explication : Le format typique d'un en-tête Authorization est Bearer <token>. Le split(' ')[1] permet de récupérer le <token>.
# 6. payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
# Fonctionnement : Cette ligne décode le token JWT en utilisant la clé secrète définie dans settings.SECRET_KEY et l'algorithme HS256. Le résultat est un dictionnaire qui contient les données (appelées payload) du token.
# Explication : Le token JWT contient des informations comme l'identifiant de l'utilisateur, l'expiration du token, etc. Ici, le middleware essaie de décoder le token pour récupérer ces informations.
# 7. user_id = payload.get('user_id')
# Fonctionnement : Une fois le payload décodé, cette ligne récupère l'identifiant de l'utilisateur (user_id) à partir des données du token.
# Explication : Le payload contient probablement des informations personnalisées, comme user_id, qui est nécessaire pour identifier l'utilisateur associé au token.
# 8. user = CustomUser.objects.get(id=user_id)
# Fonctionnement : Cette ligne tente de récupérer l'utilisateur correspondant à l'ID extrait du token JWT en interrogeant la base de données avec CustomUser.objects.get(id=user_id).
# Explication : CustomUser est probablement un modèle personnalisé représentant un utilisateur dans la base de données. Cette ligne recherche l'utilisateur ayant l'ID récupéré à l'étape précédente.
# 9. request.user = user
# Fonctionnement : Si l'utilisateur a été trouvé, l'utilisateur est attaché à la requête via request.user. Cela permet à la vue (ou à d'autres middlewares) d'accéder à l'utilisateur authentifié.
# Explication : Une fois l'utilisateur récupéré, il est assigné à request.user, ce qui permet de l'utiliser dans la logique de la vue qui suit.
# 10. Gestion des erreurs
# except (IndexError, jwt.DecodeError, jwt.ExpiredSignatureError, CustomUser.DoesNotExist):
# Fonctionnement : Si une erreur se produit pendant l'extraction ou le décodage du token (par exemple, si le token est malformé, expiré ou si l'utilisateur n'existe pas), cette ligne intercepte ces exceptions.
# Explication : Si l'une de ces erreurs se produit, cela signifie que l'authentification a échoué, et l'utilisateur sera traité comme un utilisateur anonyme.
# 11. request.user = AnonymousUser()
# Fonctionnement : Si une erreur s'est produite ou si le token n'est pas valide, request.user est défini comme un objet AnonymousUser, représentant un utilisateur non authentifié.
# Explication : Cela permet d'éviter que le code échoue et garantit que même en cas de problème avec le token, la requête peut toujours continuer.
# 12. response = self.get_response(request)
# Fonctionnement : Après avoir traité la requête (en l'authentifiant ou en définissant un utilisateur anonyme), le middleware passe la requête à la fonction suivante de la chaîne de middlewares (ou à la vue, si c'est la fin de la chaîne).
# Explication : Cela permet à la requête d'être traitée normalement, après que l'authentification ait été effectuée.
# 13. return response
# Fonctionnement : Enfin, la réponse obtenue à partir de la chaîne de middlewares ou de la vue est retournée.
# Explication : Cela renvoie la réponse du serveur au client après avoir traité la requête.