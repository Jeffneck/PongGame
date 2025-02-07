# # game/views/tournamentLocal.py

# import logging
# from django.views import View
# from django.http import JsonResponse
# from django.utils.decorators import method_decorator
# from django.views.decorators.csrf import csrf_protect
# from django.template.loader import render_to_string
# from django.shortcuts import get_object_or_404
# from django.templatetags.static import static  
# from pong_project.decorators import login_required_json

# from game.forms import TournamentParametersForm
# from game.models import (
#     LocalTournament, 
#     GameSession, 
#     GameParameters
# )
# from game.manager import schedule_game

# logger = logging.getLogger(__name__)

# @method_decorator(csrf_protect, name='dispatch')
# @method_decorator(login_required_json, name='dispatch')
# class CreateTournamentView(View):
#     """
#     Gère l'affichage (GET) du formulaire de création de tournoi,
#     et la création (POST) d'un nouveau LocalTournament.
#     """
#     def get(self, request):
#         # Crée un formulaire basé sur TournamentParametersForm
#         form = TournamentParametersForm()
        
#         # On rend un template HTML qui contient un <form> 
#         # (par exemple : 'game/tournament/select_players.html')
#         rendered_html = render_to_string(
#             'game/tournament/select_players.html',
#             {'form': form},
#             request=request
#         )
        
#         return JsonResponse({
#             'status': 'success',
#             'html': rendered_html,
#         })
    
#     def post(self, request):
#         # On récupère les données envoyées par le front
#         form = TournamentParametersForm(request.POST)
        
#         if not form.is_valid():
#             logger.debug("FORM INVALIDE CREATE TOURNAMENT")
#             return JsonResponse({
#                 'status': 'error',
#                 'message': 'Formulaire invalide.',
#                 'errors': form.errors,
#             }, status=400)
        
#         # Sauvegarde en BDD du LocalTournament + TournamentParameters (via le form)
#         tournament = form.save()
#         logger.debug(f"[CreateTournamentView] Tournoi {tournament.id} créé avec succès.")
        
#         return JsonResponse({
#             'status': 'success',
#             'tournament_id': str(tournament.id),
#             'message': f"Tournoi {tournament.name} créé avec succès.",
#         }, status=201)



# @method_decorator(csrf_protect, name='dispatch')
# @method_decorator(login_required_json, name='dispatch')
# class TournamentBracketView(View):
#     """
#     Récupère l'état (status) du tournoi + le bracket (HTML).
#     Correspond à GET /game/tournament_bracket/<tournament_id>.
#     """
#     def get(self, request, tournament_id):
#         tournament = get_object_or_404(LocalTournament, id=tournament_id)

#         # Par exemple, status peut être "pending", "semifinal1_in_progress", "finished", etc.
#         status = tournament.status

#         # Construction du dictionnaire des avatars avec des URLs statiques résolues
#         player_avatars = {
#             tournament.player1: static('svg/astronaut_gang.svg'),
#             tournament.player2: static('svg/shark_dumbble.svg'),
#             tournament.player3: static('svg/monkey_money.svg'),
#             tournament.player4: static('svg/death_bath.svg'),
#         }

#         # Contexte minimal pour afficher le bracket (les gagnants, le status, etc.)
#         tournament_context = {
#             'tournament_status': status,
#         }

#         # Injection du contexte dans le template (ici, par exemple, "tournament_bracket.html")
#         rendered_html = render_to_string('game/tournament/tournament_bracket.html')

#         return JsonResponse({
#             'status': 'success',
#             'html': rendered_html,
#             'tournament_status': status,
#             'tournament_name': tournament.name,
#             'player1': tournament.player1,
#             'player2': tournament.player2,
#             'player3': tournament.player3,
#             'player4': tournament.player4,
#             'winner_semifinal_1': tournament.winner_semifinal_1,
#             'winner_semifinal_2': tournament.winner_semifinal_2,
#             'winner_final': tournament.winner_final,
#             'player_avatars': player_avatars,  # Envoi des URLs résolues
#         }, status=200)


# @method_decorator(csrf_protect, name='dispatch')
# @method_decorator(login_required_json, name='dispatch')
# class TournamentNextGameView(View):
#     """
#     Renvoie (en GET) le prochain match à jouer: ex. "semifinal1", "semifinal2", "final", ou "finished".
#     Correspond à GET /game/tournament_next_game/<tournament_id>.
#     """
#     def get(self, request, tournament_id):
#         tournament = get_object_or_404(LocalTournament, id=tournament_id)
#         tournament_status = tournament.status
#         logger.error(tournament_status)
#         # Si le tournoi est déjà fini, on renvoie quelque chose d'explicite
#         if tournament_status == "finished":
#             return JsonResponse({
#                 'status': 'success',
#                 'html': "<p>Le tournoi est terminé !</p>",
#                 'next_match_type': 'finished',
#             }, status=200)

#         # Mapping logique interne: 
#         match_mapping = {
#             'pending': 'semifinal1',
#             'semifinal1_done': 'semifinal2',
#             'semifinal2_done': 'final',
#         }
#         next_match_type = match_mapping.get(tournament_status, None)
#         logger.error(next_match_type)
#         if not next_match_type:
#             return JsonResponse({
#                 'status': 'error',
#                 'message': f"Type de match invalide ou introuvable pour le statut : {tournament_status}",
#             }, status=400)
        
#         if next_match_type == 'finished':
#             return JsonResponse({
#                 'status': 'success',
#                 'html': "<p>Le tournoi est terminé !</p>",
#                 'next_match_type': 'finished',
#             }, status=200)
        
#         # En fonction du match, on détermine les joueurs "left" / "right"
#         if next_match_type == 'semifinal1':
#             player_left = tournament.player1
#             player_right = tournament.player2
#         elif next_match_type == 'semifinal2':
#             player_left = tournament.player3
#             player_right = tournament.player4
#         elif next_match_type == 'final':
#             # On récupère les gagnants des 2 demi-finales
#             player_left = tournament.winner_semifinal_1 
#             player_right = tournament.winner_semifinal_2
#         else:
#             player_left, player_right = "???", "???"
        
#         # Contexte pour votre template
#         next_game_context = {
#             'next_match_type': next_match_type,
#             'player_left': player_left,
#             'player_right': player_right,
#         }
        
#         rendered_html = render_to_string(
#             'game/tournament/tournament_next_game.html',
#             next_game_context,
#             request=request
#         )
        
#         return JsonResponse({
#             'status': 'success',
#             'html': rendered_html,
#             'next_match_type': next_match_type,
#         }, status=200)

# @method_decorator(csrf_protect, name='dispatch')
# @method_decorator(login_required_json, name='dispatch')
# class CreateTournamentGameSessionView(View):
#     """
#     Crée une GameSession (semifinal1, semifinal2 ou final) pour le tournoi <tournament_id>.
#     Copy les TournamentParameters -> GameParameters.
#     Correspond à POST /game/create_tournament_game_session/<tournament_id>.
#     """
#     def post(self, request, tournament_id):
#         tournament = get_object_or_404(LocalTournament, id=tournament_id)
        
#         # Le front nous envoie next_match_type (ex: semifinal1, semifinal2, final)
#         next_match_type = request.POST.get('next_match_type')
        
#         if not tournament.parameters:
#             return JsonResponse({
#                 'status': 'error',
#                 'message': "Ce tournoi ne dispose pas de TournamentParameters.",
#             }, status=400)

#         # On choisit quels joueurs se retrouvent en left / right
#         if next_match_type == 'semifinal1':
#             player_left_local = tournament.player1
#             player_right_local = tournament.player2
#             tournament.status = 'semifinal1_in_progress'
#         elif next_match_type == 'semifinal2':
#             player_left_local = tournament.player3
#             player_right_local = tournament.player4
#             tournament.status = 'semifinal2_in_progress'
#         elif next_match_type == 'final':
#             # On suppose que winner_semifinal_1 / _2 sont déjà set
#             player_left_local = tournament.winner_semifinal_1
#             player_right_local = tournament.winner_semifinal_2
#             if not player_left_local or not player_right_local:
#                 return JsonResponse({
#                     'status': 'error',
#                     'message': "Impossible de créer la finale: gagnants des demi-finales non définis.",
#                 }, status=400)
#             tournament.status = 'final_in_progress'
#         else:
#             return JsonResponse({
#                 'status': 'error',
#                 'message': f"Type de match invalide: {next_match_type}",
#             }, status=400)
        
#         # Création de la GameSession "local" (pas online) 
#         game_session = GameSession.objects.create(
#             status='waiting',
#             is_online=False,
#             player_left_local=player_left_local,
#             player_right_local=player_right_local,
#             tournament_id=str(tournament.id)  # On stocke l'id du tournoi
#         )

#         # Copier params du LocalTournament vers la GameSession
#         tparams = tournament.parameters
#         GameParameters.objects.create(
#             game_session=game_session,
#             ball_speed=tparams.ball_speed,
#             paddle_size=tparams.paddle_size,
#             bonus_enabled=tparams.bonus_enabled,
#             obstacles_enabled=tparams.obstacles_enabled,
#         )

#         # On relie la GameSession à la bonne clé dans LocalTournament
#         if next_match_type == 'semifinal1':
#             tournament.semifinal1 = game_session
#         elif next_match_type == 'semifinal2':
#             tournament.semifinal2 = game_session
#         else:  # final
#             tournament.final = game_session
        
#         tournament.save()

#         logger.debug(f"[CreateTournamentGameSessionView] Crée GameSession {game_session.id} pour {next_match_type}.")

#         # Optionnel: un snippet HTML à injecter (par ex. un canvas de jeu, etc.)
#         context = {
#             'player_left_name': player_left_local ,# default player 1
#             'player_right_name': player_right_local # defaut player 2,
#         }
#         rendered_html = render_to_string(
#             'game/live_game.html',
#             context
#         )

#         return JsonResponse({
#             'status': 'success',
#             'message': f"{next_match_type} créée pour le tournoi {tournament.name}.",
#             'game_id': str(game_session.id),
#             'html': rendered_html,
#             'tournament_status': tournament.status,
#         }, status=201)

# @method_decorator(csrf_protect, name='dispatch')
# @method_decorator(login_required_json, name='dispatch')
# class StartTournamentGameSessionView(View):
#     """
#     Lance la GameSession (status=running) et appelle schedule_game pour la boucle.
#     Correspond à POST /game/start_tournament_game_session/<game_id>.
#     """
#     def post(self, request, game_id):
#         try:
#             session = GameSession.objects.get(id=game_id)
#         except GameSession.DoesNotExist:
#             return JsonResponse({
#                 'status': 'error',
#                 'message': "La session de jeu spécifiée n'existe pas.",
#             }, status=404)

#         # On s'assure que c'est bien local (pas online)
#         if session.is_online:
#             return JsonResponse({
#                 'status': 'error',
#                 'message': "Cette session est en ligne, impossible de la lancer avec l'API locale.",
#             }, status=400)

#         if session.status == 'running':
#             return JsonResponse({
#                 'status': 'error',
#                 'message': f"La partie {game_id} est déjà en cours.",
#             }, status=400)

#         if session.status == 'finished':
#             return JsonResponse({
#                 'status': 'error',
#                 'message': f"La partie {game_id} est déjà terminée.",
#             }, status=400)

#         # On lance la loop de jeu asynchrone
#         schedule_game(str(session.id))

#         # Mettre la session en état "running"
#         session.status = 'running'
#         # le bouton a ete appuye ce qui signifie que les 2 joueurs sont prets (en local)
#         session.ready_left = True
#         session.ready_right = True
#         session.save()

#         return JsonResponse({
#             'status': 'success',
#             'message': f"Partie {game_id} lancée avec succès."
#         })



# gameTournament.py
import logging
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from django.templatetags.static import static  
from pong_project.decorators import login_required_json
from game.forms import TournamentParametersForm
from game.models import LocalTournament, GameSession, GameParameters
from game.manager import schedule_game

logger = logging.getLogger(__name__)

@method_decorator(csrf_protect, name='dispatch')
@method_decorator(login_required_json, name='dispatch')
class CreateTournamentView(View):
    """
    Affiche le formulaire de création de tournoi et crée un nouveau tournoi.
    """
    def get(self, request):
        try:

            form = TournamentParametersForm()
            if request.POST.get('is_touch', 'false') == "true":
                return JsonResponse({'status': 'error', 'message': 'Mode non disponible pour le tactile'}, status=403)
            rendered_html = render_to_string('game/tournament/select_players.html', {'form': form}, request=request)
            return JsonResponse({'status': 'success', 'html': rendered_html}, status=200)
        except Exception as e:
            logger.exception("Error in CreateTournamentView GET: %s", e)
            return JsonResponse({'status': 'error', 'message': 'Internal server error'}, status=500)
    
    def post(self, request):
        try:
            form = TournamentParametersForm(request.POST)
            if not form.is_valid():
                logger.debug("Formulaire de tournoi invalide: %s", form.errors)
                return JsonResponse({'status': 'error', 'message': 'Formulaire invalide.', 'errors': form.errors}, status=400)
            tournament = form.save()
            logger.info(f"Tournament {tournament.id} créé avec succès.")
            return JsonResponse({'status': 'success', 'tournament_id': str(tournament.id), 'message': f"Tournoi {tournament.name} créé avec succès."}, status=201)
        except Exception as e:
            logger.exception("Error in CreateTournamentView POST: %s", e)
            return JsonResponse({'status': 'error', 'message': 'Internal server error'}, status=500)

@method_decorator(csrf_protect, name='dispatch')
@method_decorator(login_required_json, name='dispatch')
class TournamentBracketView(View):
    """
    Récupère l'état et le bracket du tournoi.
    """
    def get(self, request, tournament_id):
        try:
            tournament = get_object_or_404(LocalTournament, id=tournament_id)
            status = tournament.status
            player_avatars = {
                tournament.player1: static('svg/astronaut_gang.svg'),
                tournament.player2: static('svg/shark_dumbble.svg'),
                tournament.player3: static('svg/monkey_money.svg'),
                tournament.player4: static('svg/death_bath.svg'),
            }
            rendered_html = render_to_string('game/tournament/tournament_bracket.html', request=request)
            return JsonResponse({
                'status': 'success',
                'html': rendered_html,
                'tournament_status': status,
                'tournament_name': tournament.name,
                'player1': tournament.player1,
                'player2': tournament.player2,
                'player3': tournament.player3,
                'player4': tournament.player4,
                'winner_semifinal_1': tournament.winner_semifinal_1,
                'winner_semifinal_2': tournament.winner_semifinal_2,
                'winner_final': tournament.winner_final,
                'player_avatars': player_avatars,
            }, status=200)
        except Exception as e:
            logger.exception("Error in TournamentBracketView: %s", e)
            return JsonResponse({'status': 'error', 'message': 'Internal server error'}, status=500)

@method_decorator(csrf_protect, name='dispatch')
@method_decorator(login_required_json, name='dispatch')
class TournamentNextGameView(View):
    """
    Renvoie le prochain match à jouer.
    """
    def get(self, request, tournament_id):
        try:
            tournament = get_object_or_404(LocalTournament, id=tournament_id)
            tournament_status = tournament.status
            if tournament_status == "finished":
                return JsonResponse({'status': 'success', 'html': "<p>Le tournoi est terminé !</p>", 'next_match_type': 'finished'}, status=200)
            match_mapping = {
                'pending': 'semifinal1',
                'semifinal1_done': 'semifinal2',
                'semifinal2_done': 'final',
            }
            next_match_type = match_mapping.get(tournament_status, None)
            if not next_match_type:
                return JsonResponse({'status': 'error', 'message': f"Type de match invalide pour le statut : {tournament_status}"}, status=400)
            if next_match_type == 'finished':
                return JsonResponse({'status': 'success', 'html': "<p>Le tournoi est terminé !</p>", 'next_match_type': 'finished'}, status=200)
            if next_match_type == 'semifinal1':
                player_left = tournament.player1
                player_right = tournament.player2
            elif next_match_type == 'semifinal2':
                player_left = tournament.player3
                player_right = tournament.player4
            elif next_match_type == 'final':
                player_left = tournament.winner_semifinal_1 
                player_right = tournament.winner_semifinal_2
            else:
                player_left, player_right = "???", "???"
            next_game_context = {'next_match_type': next_match_type, 'player_left': player_left, 'player_right': player_right}
            rendered_html = render_to_string('game/tournament/tournament_next_game.html', next_game_context, request=request)
            return JsonResponse({'status': 'success', 'html': rendered_html, 'next_match_type': next_match_type}, status=200)
        except Exception as e:
            logger.exception("Error in TournamentNextGameView: %s", e)
            return JsonResponse({'status': 'error', 'message': 'Internal server error'}, status=500)

@method_decorator(csrf_protect, name='dispatch')
@method_decorator(login_required_json, name='dispatch')
class CreateTournamentGameSessionView(View):
    """
    Crée une GameSession pour le tournoi.
    """
    def post(self, request, tournament_id):
        try:
            tournament = get_object_or_404(LocalTournament, id=tournament_id)
            next_match_type = request.POST.get('next_match_type', '').strip()
            if not tournament.parameters:
                return JsonResponse({'status': 'error', 'message': "Ce tournoi ne dispose pas de TournamentParameters."}, status=400)
            if next_match_type == 'semifinal1':
                player_left_local = tournament.player1
                player_right_local = tournament.player2
                tournament.status = 'semifinal1_in_progress'
            elif next_match_type == 'semifinal2':
                player_left_local = tournament.player3
                player_right_local = tournament.player4
                tournament.status = 'semifinal2_in_progress'
            elif next_match_type == 'final':
                player_left_local = tournament.winner_semifinal_1
                player_right_local = tournament.winner_semifinal_2
                if not player_left_local or not player_right_local:
                    return JsonResponse({'status': 'error', 'message': "Impossible de créer la finale: gagnants non définis."}, status=400)
                tournament.status = 'final_in_progress'
            else:
                return JsonResponse({'status': 'error', 'message': f"Type de match invalide: {next_match_type}"}, status=400)
            
            game_session = GameSession.objects.create(
                status='waiting',
                is_online=False,
                player_left_local=player_left_local,
                player_right_local=player_right_local,
                tournament_id=str(tournament.id)
            )
            tparams = tournament.parameters
            GameParameters.objects.create(
                game_session=game_session,
                ball_speed=tparams.ball_speed,
                paddle_size=tparams.paddle_size,
                bonus_enabled=tparams.bonus_enabled,
                obstacles_enabled=tparams.obstacles_enabled,
            )
            if next_match_type == 'semifinal1':
                tournament.semifinal1 = game_session
            elif next_match_type == 'semifinal2':
                tournament.semifinal2 = game_session
            else:
                tournament.final = game_session
            tournament.save()
            logger.info(f"GameSession {game_session.id} créée pour {next_match_type}.")
            context = {'player_left_name': player_left_local, 'player_right_name': player_right_local}
            rendered_html = render_to_string('game/live_game.html', context, request=request)
            return JsonResponse({
                'status': 'success',
                'message': f"{next_match_type} créée pour le tournoi {tournament.name}.",
                'game_id': str(game_session.id),
                'html': rendered_html,
                'tournament_status': tournament.status,
            }, status=201)
        except Exception as e:
            logger.exception("Error in CreateTournamentGameSessionView: %s", e)
            return JsonResponse({'status': 'error', 'message': 'Internal server error'}, status=500)

@method_decorator(csrf_protect, name='dispatch')
@method_decorator(login_required_json, name='dispatch')
class StartTournamentGameSessionView(View):
    """
    Lance une session de jeu de tournoi.
    """
    def post(self, request, game_id):
        try:
            session = get_object_or_404(GameSession, id=game_id)
            if session.is_online:
                return JsonResponse({'status': 'error', 'message': "Cette session est en ligne, impossible de la lancer avec l'API locale."}, status=400)
            if session.status in ['running', 'finished']:
                return JsonResponse({'status': 'error', 'message': f"La partie {game_id} est déjà en cours ou terminée."}, status=400)
            schedule_game(str(session.id))
            session.status = 'running'
            session.ready_left = True
            session.ready_right = True
            session.save()
            return JsonResponse({'status': 'success', 'message': f"Partie {game_id} lancée avec succès."}, status=200)
        except Exception as e:
            logger.exception("Error in StartTournamentGameSessionView: %s", e)
            return JsonResponse({'status': 'error', 'message': 'Internal server error'}, status=500)
