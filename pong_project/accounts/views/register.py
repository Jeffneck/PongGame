import logging

from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST, require_GET
from django.template.loader import render_to_string

from accounts.forms import RegistrationForm

logger = logging.getLogger(__name__)

@method_decorator(csrf_protect, name='dispatch')
class RegisterView(View):
    """
    Vue pour gérer l'inscription utilisateur.
    - GET : Renvoie le formulaire d'inscription (HTML) dans une réponse JSON.
    - POST : Traite les données soumises pour créer un nouvel utilisateur.
    """
    @method_decorator(require_GET)
    def get(self, request):
        """
        Retourne le formulaire d'inscription sous forme de fragment HTML.
        """
        form = RegistrationForm()
       
        rendered_form = render_to_string('accounts/register.html', {'form': form})
        return JsonResponse({
            'status': 'success',
            'html': rendered_form,
        }, status=200)

    @method_decorator(require_POST)
    def post(self, request):
        """
        Traite la soumission du formulaire d'inscription et crée un nouvel utilisateur.
        """
        logger.debug("Données POST reçues: %s", request.POST)
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()  
    
                return JsonResponse({
                    'status': 'success',
                    'message': 'Inscription réussie.'
                }, status=201)
            except Exception as e:
                logger.exception("Erreur lors de la création de l'utilisateur.")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Erreur interne du serveur.'
                }, status=500)
        else:
            error_messages = []
            for field, errors in form.errors.items():
                error_messages.append(f"{field}: {', '.join(errors)}")
            error_message = " ".join(error_messages)
            return JsonResponse({
                'status': 'error',
                'message': error_message,
            }, status=400)
