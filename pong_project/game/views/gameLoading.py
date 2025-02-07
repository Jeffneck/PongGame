# gameLoading.py
import logging
from django.views import View
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from pong_project.decorators import login_required_json

logger = logging.getLogger(__name__)

@method_decorator(csrf_protect, name='dispatch')
@method_decorator(login_required_json, name='dispatch')
class LoadingView(View):
    """
    View pour afficher l'écran de chargement.
    - GET: Retourne le HTML de l'écran de chargement.
    - Autres méthodes: Retourne une erreur 405.
    """
    def get(self, request):
        try:
            logger.debug("Handling GET request for LoadingView")
            rendered_html = render_to_string('game/loading.html', request=request)
            return JsonResponse({'status': 'success', 'html': rendered_html}, status=200)
        except Exception as e:
            logger.exception("Error in LoadingView GET: %s", e)
            return JsonResponse({'status': 'error', 'message': 'Internal server error'}, status=500)

    def http_method_not_allowed(self, request, *args, **kwargs):
        logger.warning(f"Méthode non autorisée : {request.method} pour LoadingView")
        return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée'}, status=405)
