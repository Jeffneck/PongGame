# game/views/gameLocal
# added (tout le fichier)
import logging
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from game.models import GameSession
# import uuid
from game.forms import GameParametersForm

from game.manager import schedule_game  # Assurez-vous que vous avez un task qui gère le démarrage du jeu en background
from pong_project.decorators import login_required_json

# ---- Configuration ----
logger = logging.getLogger(__name__)


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(login_required_json, name='dispatch')
class CreateGameLocalView(View):
    """
    Gère la création d'une nouvelle GameSession et des paramètres associés pour une partie locale.
    """
    def post(self, request):
        form = GameParametersForm(request.POST)
        logger.debug("Rentre dans CREATE GAME LOCAL")
        if not form.is_valid():
            # Renvoyer une réponse JSON en cas d'erreurs dans le formulaire
            return JsonResponse({
                'status': 'error',
                'message': "Les paramètres du jeu sont invalides."
            })

        # Créer une nouvelle GameSession pour une partie locale
        session = GameSession.objects.create(status='waiting', is_online=False)
        logger.debug(session)
        # Assignation des noms des joueurs pour la partie locale (voir lacalGameForm dans form.py pour utiliser un formulaire plutot que des valeurs par defaut)
        player_left_local = "PLAYER1"
        player_right_local = "PLAYER2" 

        # Vérifier si les noms des joueurs sont fournis
        if player_left_local:
            session.player_left_local = player_left_local
        if player_right_local:
            session.player_right_local = player_right_local
        
        session.save()

        # Créer les paramètres de jeu associés à cette session
        parameters = form.save(commit=False)
        parameters.game_session = session
        parameters.save()

        # Log de la création de la session de jeu
        logger.debug(f"[create_game] GameSession {session.id} créée pour {player_left_local} et {player_right_local} avec paramètres personnalisés.")
        # Retourner l'ID de la session et un message de succès dans la réponse JSON
        
        rendered_html = render_to_string('game/local_game/live_local_game.html')
        return JsonResponse({
            'status': 'success',
            'html' : rendered_html,
            'message': "Partie locale créée avec succès.",
            'game_id': str(session.id)
        }, status=201)

# lancee par l'appui sur le bouton Lancer la partie
@method_decorator(csrf_protect, name='dispatch')
@method_decorator(login_required_json, name='dispatch')
class StartLocalGameView(View):
    """
    Démarre la partie locale en exécutant la logique du jeu.
    """
    def post(self, request, game_id):
        try:
            # Récupérer la session de jeu par son ID
            session = GameSession.objects.get(id=game_id)
            print(f"[DEBUG] StartLocalGameView gameSession {session}")  # Debug

            # Vérifier que la session est une partie locale
            if session.is_online:
                return JsonResponse({
                    'status': 'error',
                    'message': "La partie en ligne ne peut pas être lancée avec cette API. Cette API sert à lancer une partie locale."
                })

            # Vérifier que la partie n'est pas déjà en cours
            if session.status == 'running':
                return JsonResponse({
                    'status': 'error',
                    'message': f"La partie {game_id} est déjà en cours."
                })
            
            # Vérifier que la partie n'est pas déjà terminée
            if session.status == 'finished':
                return JsonResponse({
                    'status': 'error',
                    'message': f"La partie {game_id} est déjà terminée et ne peut pas être relancée."
                })


            # Mettre la session en état "running"
            session.status = 'running'
            # le bouton a ete appuye ce qui signifie que les 2 joueurs sont prets (en local)
            session.ready_left = True
            session.ready_right = True
            session.save()

            schedule_game(game_id) 

            return JsonResponse({
                'status': 'success',
                'message': f"Partie {game_id} lancée avec succès."
            })

        except GameSession.DoesNotExist:
            # print(f"[DEBUG] StartLocalGameView la gameSession n'existe pas")  # Debug
            return JsonResponse({
                'status': 'error',
                'message': "La session de jeu spécifiée n'existe pas."
            })
