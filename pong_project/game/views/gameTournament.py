
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


@method_decorator(csrf_protect, name='dispatch')
class CreateTournamentView(View):
    """
    Reçoit un POST avec:
      - name, player1..4
      - ball_speed, paddle_size, bonus_enabled, obstacles_enabled
    Crée un LocalTournament + TournamentParameters.
    Retourne du JSON avec l'ID du tournoi, etc.
    """
    def post(self, request):
        form = TournamentParametersForm(request.POST)
        if not form.is_valid():
            return JsonResponse({
                'status': 'error',
                'message': 'Formulaire invalide.',
                'errors': form.errors
            }, status=400)

        tournament = form.save()
        logger.debug(f"[CreateLocalTournamentView] Tournoi {tournament.id} créé avec succès.")

        # Optionnel: on peut renvoyer un snippet HTML (ou un simple message)
        rendered_html = render_to_string(
            'game/tournament/local_tournament_created.html',
            {'tournament': tournament},
            request=request
        )

        return JsonResponse({
            'status': 'success',
            'tournament_id': str(tournament.id),
            'html': rendered_html,
            'message': f"Tournoi {tournament.name} créé avec succès."
        }, status=201)




@method_decorator(csrf_protect, name='dispatch')
class CreateTournamentGameSessionView(View):
    """
    Crée la GameSession (semi1, semi2 ou finale) pour le tournoi <tournament_id>.
    Copie les TournamentParameters dans le GameParameters nouvellement créé.
    """
    def post(self, request, tournament_id):
        match_type = request.POST.get('match_type')  # e.g. "semifinal1"
        tournament = get_object_or_404(LocalTournament, id=tournament_id)

        if not tournament.parameters:
            return JsonResponse({
                'status': 'error',
                'message': "Ce tournoi ne dispose pas de TournamentParameters."
            }, status=400)

        # On détermine quels joueurs placer en "left" / "right"
        if match_type == 'semifinal1':
            player_left_name = tournament.player1
            player_right_name = tournament.player2
            tournament.status = 'semifinal1_in_progress'
        elif match_type == 'semifinal2':
            player_left_name = tournament.player3
            player_right_name = tournament.player4
            tournament.status = 'semifinal2_in_progress'
        elif match_type == 'final':
            # Normalement, on récupère le winner de la semi1 et semi2
            # Ici, pour simplifier, on affecte directement
            # (vous pouvez y insérer la logique d'aller chercher le vainqueur via GameResult)
            player_left_name = "WinnerSemi1"  
            player_right_name = "WinnerSemi2"
            tournament.status = 'final_in_progress'
        else:
            return JsonResponse({
                'status': 'error',
                'message': f"Type de match invalide: {match_type}"
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
        if match_type == 'semifinal1':
            tournament.semifinal1 = game_session
        elif match_type == 'semifinal2':
            tournament.semifinal2 = game_session
        else:  # final
            tournament.final = game_session

        tournament.save()

        logger.debug(f"[CreateTournamentGameSessionView] Crée GameSession {game_session.id} pour {match_type}.")

        # On peut éventuellement renvoyer un fragment HTML pour l'affichage
        rendered_html = render_to_string(
            'game/tournament/live_tournament_game.html',
            {'game_id': game_session.id},
            request=request
        )

        return JsonResponse({
            'status': 'success',
            'message': f"{match_type} créée pour le tournoi {tournament.name}.",
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
