# gameHome.py
import logging
from django.views import View
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from pong_project.decorators import login_required_json

logger = logging.getLogger(__name__)

@method_decorator(csrf_protect, name='dispatch')
@method_decorator(login_required_json, name='dispatch')
class GameHomeView(View):
    """
    View pour afficher la page d'accueil du jeu.
    - GET: Retourne le HTML de la page de jeu.
    - Autres méthodes: Retourne une erreur 405.
    """
    def get(self, request):
        try:
            logger.debug("Handling GET request for GameHomeView")
            rendered_html = render_to_string('game/gameHome.html', request=request)
            return JsonResponse({'status': 'success', 'html': rendered_html}, status=200)
        except Exception as e:
            logger.exception("Error in GameHomeView GET: %s", e)
            return JsonResponse({'status': 'error', 'message': 'Internal server error'}, status=500)

    def http_method_not_allowed(self, request, *args, **kwargs):
        logger.warning(f"Méthode non autorisée : {request.method} pour GameHomeView")
        return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée'}, status=405)
