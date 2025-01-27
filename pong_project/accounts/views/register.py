# ---- Imports standard ----
import logging

# ---- Imports tiers ----
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string

# ---- Imports locaux ----
from accounts.forms import RegistrationForm

# ---- Configuration ----
logger = logging.getLogger(__name__)

# @method_decorator(csrf_protect, name='dispatch')  # Applique la protection CSRF à toutes les méthodes de la vue
class RegisterView(View):
    """
    Class-Based View (CBV) pour gérer l'inscription utilisateur.
    - GET : Renvoie un formulaire d'inscription sous forme de HTML encapsulé dans une réponse JSON.
    - POST : Traite les données soumises pour inscrire un nouvel utilisateur.
    """

    def get(self, request):
        """
        Gère une requête HTTP GET.
        Retourne un formulaire d'inscription sous forme de fragment HTML.
        """
        form = RegistrationForm()  # Initialise un formulaire d'inscription vide
        rendered_form = render_to_string('accounts/register.html')  # Génère le HTML du formulaire
        return JsonResponse({
            'status': 'success',
            'html': rendered_form,  # HTML à injecter côté client
        })

    @method_decorator(require_POST) 
    def post(self, request):
        """
        Gère une requête HTTP POST.
        Traite les données du formulaire, crée un nouvel utilisateur et retourne une réponse JSON.
        """
        logger.debug(f"request.POST: {request.POST}")
        form = RegistrationForm(request.POST)  # Remplit le formulaire avec les données soumises
        if form.is_valid():
            # Crée un nouvel utilisateur sans encore sauvegarder dans la base de données
            user = form.save()
            user.save()  # Sauvegarde l'utilisateur dans la base de données
            return JsonResponse({'status': 'success', 'message': 'Inscription réussie.'})
        # Retourne les erreurs de validation du formulaire sous forme de JSON
        return JsonResponse({'status': 'error', 'errors': form.errors})


# Le principe des Class-Based Views (CBV) :
# Les CBV sont une alternative aux Function-Based Views (FBV) dans Django. Elles permettent d’organiser la logique de gestion des requêtes HTTP dans une classe au lieu d’une simple fonction.
# Chaque méthode HTTP (comme GET, POST, etc.) correspond à une méthode distincte dans la classe (get, post, etc.), ce qui améliore la lisibilité et la maintenabilité.
# Les CBV facilitent l’utilisation de l’héritage, permettant de réutiliser et d’étendre des comportements communs (par exemple, des mixins ou des vues génériques).