# game/views.py

import logging
from django.views import View
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from pong_project.decorators import login_required_json

from game.forms import GameParametersForm
from game.models import GameSession

logger = logging.getLogger(__name__)

@method_decorator(csrf_protect, name='dispatch')
@method_decorator(login_required_json, name='dispatch')
class GameMenuView(View):

    def get(self, request):
        logger.debug("Handling GET request for GameMenuView")

        form = GameParametersForm()

        rendered_html = render_to_string('game/gameMenu.html', {'form': form}, request)
        return JsonResponse({
            'status': 'success',
            'html': rendered_html
        })


    def http_method_not_allowed(self, request, *args, **kwargs):
        logger.warning(f"Méthode non autorisée : {request.method} pour GameMenuView")
        return JsonResponse({
            'status': 'error',
            'message': 'Méthode non autorisée'
        }, status=405)


