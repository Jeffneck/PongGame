from django.views import View
from django.http import JsonResponse
from django.utils.translation import activate
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
import logging

logger = logging.getLogger(__name__)

@method_decorator(csrf_protect, name='dispatch')
class SetLanguageView(View):
    """
    Handle language changes for the user.
    """

    def post(self, request):
        try:
            # Récupérer la langue depuis les données POST
            language = request.POST.get('language')

            if not language:
                return JsonResponse({'status': 'error', 'message': 'No language specified.'}, status=400)

            # Activer la langue
            activate(language)

            # Enregistrer dans la session si disponible
            if hasattr(request, 'session'):
                request.session['django_language'] = language
            
            response = JsonResponse({'status': 'success', 'message': f'Language changed to {language}.'})
            response.set_cookie('django_language', language)
            return response

            #return JsonResponse({'status': 'success', 'message': f'Language changed to {language}.'}, status=200)

        except Exception as e:
            # Log l'erreur et retourner une réponse JSON d'erreur
            logger.error(f"Error in SetLanguageView: {e}")
            return JsonResponse({'status': 'error', 'message': 'An error occurred while changing the language.'}, status=500)
