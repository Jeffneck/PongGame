from django.views import View
from django.http import JsonResponse
from django.utils.translation import activate
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
import logging
from pong_project.decorators import login_required_json
from django.utils.translation import gettext_lazy as _
logger = logging.getLogger(__name__)

@method_decorator(csrf_protect, name='dispatch')  # Applique la protection CSRF à toutes les méthodes de la classe
@method_decorator(login_required_json, name='dispatch')  # Restreint l'accès à la vue aux utilisateurs connectés
class SetLanguageView(View):
    """
    Handle language changes for the user.
    """

    def post(self, request):
        try:
            # Récupérer la langue depuis les données POST
            language = request.POST.get('language')

            if not language:
                return JsonResponse({'status': 'error', 'message': _('Pas de langage spécifié.')}, status=400)

            # Activer la langue
            activate(language)

            # Enregistrer dans la session si disponible
            if hasattr(request, 'session'):
                request.session['django_language'] = language
            
            response = JsonResponse({'status': 'success', 'message': _(f'Language changed to) {language}.')})
            response.set_cookie('django_language', language)
            return response

            #return JsonResponse({'status': 'success', 'message': f'Language changed to {language}.'}, status=200)

        except Exception as e:
            # Log l'erreur et retourner une réponse JSON d'erreur
            return JsonResponse({'status': 'error', 'message': _('An error occurred while changing the language.')}, status=500)
