# game/views/gameStatus
import logging
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from game.models import GameSession

from pong_project.decorators import login_required_json

# ---- Configuration ----
logger = logging.getLogger(__name__)


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(login_required_json, name='dispatch')
class GetGameStatusView(View):
    def get(self, request, game_id):
        try:
            session = GameSession.objects.get(id=game_id)
        except GameSession.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': "La session de jeu spécifiée n'existe pas."
            }, status=404)

        return JsonResponse({
            'status': 'success',
            'session_status': session.status 
        }, status=200)