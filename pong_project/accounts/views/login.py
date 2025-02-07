import logging

from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST, require_GET
from django.template.loader import render_to_string
from django.contrib.auth import authenticate, login
from django.utils.translation import gettext_lazy as _

from accounts.utils import generate_jwt_token
from accounts.forms import LoginForm
from pong_project.decorators import user_not_authenticated

logger = logging.getLogger(__name__)


@method_decorator(user_not_authenticated, name='dispatch')
@method_decorator(csrf_protect, name='dispatch')
class LoginView(View):
    """
    Vue pour gérer la connexion utilisateur.
    - GET  : Retourne le formulaire de connexion.
    - POST : Traite la soumission du formulaire et authentifie l'utilisateur.
    """
    @method_decorator(require_GET)
    def get(self, request):
        """
        Affiche le formulaire de connexion.
        Retourne un JSON contenant le HTML du formulaire.
        """
        form = LoginForm()
        rendered_form = render_to_string('accounts/login.html', {'form': form})
        return JsonResponse({
            'status': 'success',
            'html': rendered_form,
        }, status=200)

    @method_decorator(require_POST)
    def post(self, request):
        logger.debug("Début de la méthode POST de LoginView")
        form = LoginForm(request.POST)

        if not form.is_valid():
            return JsonResponse(
                {'status': 'error', 'errors': form.errors},
                status=400
            )

            if user is not None:
                if user.is_active:
                    request.session['user_id'] = user.id

        user = authenticate(request, username=username, password=password)

        # Message d'erreur générique pour éviter l'énumération d'utilisateurs
        error_message = _("Nom d'utilisateur ou mot de passe invalide")

        # Vérification de l'existence et de l'activité du compte
        if user is None or not user.is_active:
            logger.warning("Tentative d'authentification échouée pour l'utilisateur: %s", username)
            return JsonResponse(
                {'status': 'error', 'message': error_message, 'error_code': 'not_authenticated'},
                status=401
            )

                    return JsonResponse({
                        'status': 'success',
                        'access_token': token_jwt['access_token'],
                        'refresh_token': token_jwt['refresh_token'],
                        'requires_2fa': False,
                        'ís_authenticated': True
                    })
                else:
                    return JsonResponse({'status': 'error', 'message': _('Compte désactivé')})

            # Invalid credentials
            return JsonResponse({'status': 'error', 'message': _('Identifiants incorrects')})

            # Mise à jour du statut de l'utilisateur et authentification
            user.is_online = True
            user.save()
            login(request, user)

            response_data = {
                'status': 'success',
                'access_token': token_jwt.get('access_token'),
                'refresh_token': token_jwt.get('refresh_token'),
                'requires_2fa': False,
                'is_authenticated': True
            }
            return JsonResponse(response_data, status=200)
        except Exception as e:
            logger.exception("Erreur lors de l'authentification pour l'utilisateur: %s", username)
            return JsonResponse(
                {'status': 'error', 'message': _("Erreur interne du serveur")},
                status=500
            )
