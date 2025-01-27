# ---- Imports standard ----
import logging

# ---- Imports tiers ----
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.contrib.auth import authenticate, login

# ---- Imports locaux ----
from accounts.utils import generate_jwt_token
from accounts.forms import LoginForm
from transcendence.decorators import user_not_authenticated


# ---- Configuration ----
logger = logging.getLogger(__name__)

@method_decorator(user_not_authenticated, name='dispatch')  # Applique le décorateur user_not_authenticated à toute la classe
@method_decorator(csrf_protect, name='dispatch')  # Applique la protection CSRF à toute la classe
class LoginView(View):
    """
    Class-Based View (CBV) pour gérer la connexion utilisateur.
    - GET : Affiche le formulaire de connexion.
    - POST : Traite les données du formulaire et connecte l'utilisateur.
    """

    #[IMPROVE] Appliquer le form avec balises django dans le html
    def get(self, request):
        """
        Gère une requête HTTP GET.
        Retourne un formulaire de connexion sous forme de HTML encapsulé dans une réponse JSON.
        """
        form = LoginForm()  # Initialise un formulaire de connexion vide
        # Le HTML est transforme en string et le formulaire renvoye est lie au regles du back (cf.forms.py) 
        rendered_form = render_to_string('accounts/login.html', {'form': form}) #ce retour implique d'utiliser les balises django dans le html
        return JsonResponse({
            'status': 'success',
            'html': rendered_form,  # Renommé pour être plus explicite
        })

    @method_decorator(require_POST)  # Restreint cette méthode aux requêtes POST uniquement
    def post(self, request):
        logger.debug("Entering SubmitLoginView POST")

        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Authenticate the user
            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_active:
                    logger.debug("User is active")
                    request.session['user_id'] = user.id

                    # Check if 2FA is enabled
                    if user.is_2fa_enabled:
                        request.session['auth_partial'] = True
                        return JsonResponse({'status': 'success', 'requires_2fa': True})

                    # Generate JWT token, contient les deux tokens (access et refresh)
                    token_jwt = generate_jwt_token(user)

                    # Update user status and login
                    user.is_online = True
                    user.save()
                    login(request, user)
                    # logger.debug(request.user.is_authenticated)

                    return JsonResponse({
                        'status': 'success',
                        'access_token': token_jwt['access_token'],
                        'refresh_token': token_jwt['refresh_token'],
                        'requires_2fa': False,
                        'ís_authenticated': True
                    })
                else:
                    return JsonResponse({'status': 'error', 'message': 'Compte désactivé'})

            # Invalid credentials
            return JsonResponse({'status': 'error', 'message': 'Identifiants incorrects'})

        # Return form validation errors
        return JsonResponse({'status': 'error', 'errors': form.errors})