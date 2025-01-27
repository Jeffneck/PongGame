# game/views.py

import logging
from django.views import View
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

from game.forms import GameParametersForm
from game.models import GameSession

logger = logging.getLogger(__name__)

@method_decorator(csrf_protect, name='dispatch')
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




#----------- Ici créer une vue pour récupérer les paramètres de jeu -----------#

class CreateGameLocalView(View):
    """
    Handles the creation of a new GameSession and associated parameters.
    """
    def post(self, request):
        form = GameParametersForm(request.POST)
        
        if not form.is_valid():
            # Render le formulaire avec les erreurs pour l'inclure dans la réponse JSON
            return JsonResponse({
                'status': 'error',
                'message': "Les paramètres du jeu sont invalides."
            })

        # Créer une nouvelle GameSession
        session = GameSession.objects.create(status='waiting')
        game_id = str(session.id)

        # Créer les GameParameters liés à cette session
        parameters = form.save(commit=False)
        parameters.game_session = session
        parameters.save()

        # Log de la création de session
        print(f"[create_game] GameSession {game_id} created avec paramètres personnalisés.")

        return JsonResponse({
            'status': 'success',
            'message': "Partie créée avec succès.",
            'game_id': game_id
        }, status=201)