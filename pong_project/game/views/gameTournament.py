
# game/views/tournamentLocal.py

import logging
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404

from game.forms import TournamentParametersForm
from game.models import (
    LocalTournament, 
    GameSession, 
    GameParameters
)
from game.manager import schedule_game

logger = logging.getLogger(__name__)

# Lancée par le bouton Lancer Tournoi du GameMenu
# creer le tournoi après la reception des parametres de tournoi et du nom des players
@method_decorator(csrf_protect, name='dispatch')
class CreateTournamentView(View):
    """
    Reçoit un POST avec:
      - name, player1..4
      - ball_speed, paddle_size, bonus_enabled, obstacles_enabled
    Crée un LocalTournament + TournamentParameters.
    Retourne du JSON avec l'ID du tournoi, etc.
    """

    def get(self, request):
        form = TournamentParametersForm()
        rendered_html = render_to_string(
            'game/tournament/select_players.html',
            {'form': form},  # Corrected: Form should be in a dictionary
            request=request
        )
        return JsonResponse({
            'status': 'success',
            'html': rendered_html,
        })

    def post(self, request):
        form = TournamentParametersForm(request.POST)
        if not form.is_valid():
            logger.debug("FORM INVALIDE CREATE TOURNAMENT")
            return JsonResponse({
                'status': 'error',
                'message': 'Formulaire invalide.',
                'errors': form.errors
            }, status=400)

        tournament = form.save()
        logger.debug(f"[CreateLocalTournamentView] Tournoi {tournament.id} créé avec succès.")

        return JsonResponse({
            'status': 'success',
            'tournament_id': str(tournament.id),
            'message': f"Tournoi {tournament.name} créé avec succès."
        }, status=201)


# retourner au js le contexte du tournoi
# permettra d'afficher le bracket et next_tournament_game avec les bons inputs
# @method_decorator(csrf_protect, name='dispatch')
# class ExtractTournamentContext(View):
#     """
#     Affiche le bracket du tournoi avec la bonne mise en forme.
#     """

#     def get(self, request, tournament_id):
#         tournament = get_object_or_404(LocalTournament, id=tournament_id)

#         # Création du contexte pour la vue
#         tournament_context = {
#             'tournament_status': tournament.status,  # ex: "semifinal1"
#             'winner_semifinal_1': tournament.winner_semifinal_1,  # joueur ou None
#             'winner_semifinal_2': tournament.winner_semifinal_2,  # joueur ou None
#             'winner_final': tournament.winner_final,  # joueur ou None
#         }

#         # Logger pour le suivi des erreurs ou des retours
#         logger.debug(f"Tournoi {tournament_id} récupéré avec statut {tournament.status}")

#         # Génération du snippet HTML avec le contexte du tournoi
#         rendered_html = render_to_string(
#             'game/tournament/tournament_bracket.html', 
#             tournament_context, 
#             request=request  # Permet d’inclure les balises {{ request }}
#         )

#         return JsonResponse({
#             'status': 'success',
#             'tournament_context': tournament_context,
#             'html': rendered_html  # Inclusion du rendu HTML dans la réponse JSON
#         }, status=200)


@method_decorator(csrf_protect, name='dispatch')
class TournamentBracketView(View):
    """
    Affiche le bracket du tournoi avec la bonne mise en forme.
    """

    def get(self, request, tournament_id):
        # Récupérer le tournoi ou renvoyer une 404
        tournament = get_object_or_404(LocalTournament, id=tournament_id)

        # Construction du contexte du tournoi
        tournament_context = {
            'tournament_status': tournament.status,  # "semifinal1", "final", etc.
            'winner_semifinal_1': tournament.winner_semifinal_1,  # Joueur ou None
            'winner_semifinal_2': tournament.winner_semifinal_2,  # Joueur ou None
            'winner_final': tournament.winner_final,  # Joueur ou None
        }

        # Logger pour suivre l'affichage des brackets
        logger.debug(f"Affichage du bracket pour le tournoi {tournament_id}, statut: {tournament.status}")

        # Génération du HTML en injectant le contexte
        rendered_html = render_to_string(
            'game/tournament/tournament_bracket.html',
            tournament_context,
            request=request  # Permet d'utiliser {{ request }} dans le template
        )

        return JsonResponse({
            'status': 'success',
            'html': rendered_html,
        }, status=200)
    
@method_decorator(csrf_protect, name='dispatch')
class TournamentNextGameView(View):
    """
    Affiche le bracket du tournoi avec la bonne mise en forme.
    """

    def get(self, request, tournament_id):
        # Récupérer le tournoi ou renvoyer une 404
        tournament = get_object_or_404(LocalTournament, id=tournament_id)
        tournament_status = tournament.status

        # Détermination du prochain match
        match_mapping = {
            'pending': 'semifinal1',
            'semifinal1_in_progress': 'semifinal2',
            'semifinal2_in_progress': 'final',
            'final_in_progress': 'finished'
        }

        next_match_type = match_mapping.get(tournament_status, None)
        if not next_match_type:
            return JsonResponse({
                'status': 'error',
                'message': f"Type de match invalide pour le statut: {tournament_status}"
            }, status=400)

        # Détermination des joueurs en fonction du match
        if next_match_type == 'semifinal1':
            player_left = tournament.player1
            player_right = tournament.player2
        elif next_match_type == 'semifinal2':
            player_left = tournament.player3
            player_right = tournament.player4
        elif next_match_type == 'final':
            # On récupère les gagnants des demi-finales
            player_left = tournament.winner_semifinal_1 or "À déterminer"
            player_right = tournament.winner_semifinal_2 or "À déterminer"
        else:
            return JsonResponse({
                'status': 'error',
                'message': "Le tournoi est terminé."
            }, status=200)

        # Construction du contexte du prochain match
        next_game_context = {
            'next_match_type': next_match_type,
            'player_left': player_left,
            'player_right': player_right
        }

        # Logger pour le suivi des matchs
        logger.debug(f"Prochain match pour tournoi {tournament_id}: {next_match_type}")

        # Génération du HTML avec les informations du prochain match
        rendered_html = render_to_string(
            'game/tournament/tournament_next_game.html',
            next_game_context,
            request=request
        )

        return JsonResponse({
            'status': 'success',
            'html': rendered_html,
            'next_match_type': next_match_type
        }, status=200)


@method_decorator(csrf_protect, name='dispatch')
class CreateTournamentGameSessionView(View):
    """
    Crée la GameSession (semi1, semi2 ou finale) pour le tournoi <tournament_id>.
    Copie les TournamentParameters dans le GameParameters nouvellement créé.
    """
    def post(self, request, tournament_id):
        # le js nous indique quel est le prochain match à génerer dans la requete Post
        next_match_type = request.POST.get('next_match_type')  # e.g. "semifinal1"


        tournament = get_object_or_404(LocalTournament, id=tournament_id)

        if not tournament.parameters:
            return JsonResponse({
                'status': 'error',
                'message': "Ce tournoi ne dispose pas de TournamentParameters."
            }, status=400)

        # On détermine quels joueurs placer en "left" / "right"
        if next_match_type == 'semifinal1':
            player_left_name = tournament.player1
            player_right_name = tournament.player2
            tournament.status = 'semifinal1_in_progress'
        elif next_match_type == 'semifinal2':
            player_left_name = tournament.player3
            player_right_name = tournament.player4
            tournament.status = 'semifinal2_in_progress'
        elif next_match_type == 'final':
            # Normalement, on récupère le winner de la semi1 et semi2
            player_left_name = request.POST.get('winner_semifinal_1') 
            player_right_name = request.POST.get('winner_semifinal_2')
            tournament.status = 'final_in_progress'
        else:
            return JsonResponse({
                'status': 'error',
                'message': f"Type de match invalide: {next_match_type}"
            }, status=400)

        # Créer la GameSession
        game_session = GameSession.objects.create(
            status='waiting',
            is_online=False,
            player_left_name=player_left_name,
            player_right_name=player_right_name,
            tournament_id=str(tournament.id)  # On y met l'ID du tournoi
        )

        # Copier les TournamentParameters -> GameParameters
        tparams = tournament.parameters
        GameParameters.objects.create(
            game_session=game_session,
            ball_speed=tparams.ball_speed,
            paddle_size=tparams.paddle_size,
            bonus_enabled=tparams.bonus_enabled,
            obstacles_enabled=tparams.obstacles_enabled,
        )

        # Relier la session au bon champ du bracket
        if next_match_type == 'semifinal1':
            tournament.semifinal1 = game_session
        elif next_match_type == 'semifinal2':
            tournament.semifinal2 = game_session
        else:  # final
            tournament.final = game_session

        tournament.save()

        logger.debug(f"[CreateTournamentGameSessionView] Crée GameSession {game_session.id} pour {next_match_type}.")

        # On peut éventuellement renvoyer un fragment HTML pour l'affichage
        rendered_html = render_to_string(
            'game/tournament/live_tournament_game.html',
            {'game_id': game_session.id},
            request=request
        )

        return JsonResponse({
            'status': 'success',
            'message': f"{next_match_type} créée pour le tournoi {tournament.name}.",
            'game_id': str(game_session.id),
            'html': rendered_html,
            'tournament_status': tournament.status,
        }, status=201)


@method_decorator(csrf_protect, name='dispatch')
class StartTournamentGameSessionView(View):
    """
    Lance (status='running') la GameSession <game_id>, et appelle schedule_game pour la boucle de jeu.
    """
    def post(self, request, game_id):
        try:
            session = GameSession.objects.get(id=game_id)
        except GameSession.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': "La session de jeu spécifiée n'existe pas."
            }, status=404)

        # Vérifier que c'est bien une partie locale et qu'elle n'est pas déjà terminée
        if session.is_online:
            return JsonResponse({
                'status': 'error',
                'message': "Cette session est en ligne, on ne peut pas la lancer avec cette API locale."
            }, status=400)

        if session.status == 'running':
            return JsonResponse({
                'status': 'error',
                'message': f"La partie {game_id} est déjà en cours."
            }, status=400)

        if session.status == 'finished':
            return JsonResponse({
                'status': 'error',
                'message': f"La partie {game_id} est déjà terminée."
            }, status=400)

        # Démarrer la boucle de jeu (asynchrone)
        from game.manager import schedule_game
        schedule_game(str(session.id))

        # Mettre la session en "running"
        session.status = 'running'
        session.save()

        return JsonResponse({
            'status': 'success',
            'message': f"Partie {game_id} lancée avec succès."
        })
