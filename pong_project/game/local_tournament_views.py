# game/views.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import GameSession
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
import time
from .models import GameSession, GameResult, GameParameters, LocalTournament
from .manager import schedule_game
from .forms import GameParametersForm, LocalTournamentForm
from .game_loop.redis_utils import set_key
import redis
from django.conf import settings


def parameter_local_tournament(request):
    if request.method == 'POST':
        form = LocalTournamentForm(request.POST)
        if form.is_valid():
            tournament = form.save()
            tournament.save()
            
            # Ensuite, rediriger ou afficher la page du tournoi
            return redirect('detail_local_tournament', tournament_id=tournament.id)
    else:
        form = LocalTournamentForm()
    return render(request, 'game/tournament/parameter_local_tournament.html', {'form': form})


def detail_local_tournament(request, tournament_id):
    """
    Affiche le bracket du tournoi (2 demi-finales, 1 finale).
    Au bout de X secondes, on rend visible un bouton vers la prochaine étape.
    """
    tournament = get_object_or_404(LocalTournament, pk=tournament_id)

    # Récupérer les résultats éventuellement existants pour mettre à jour l'affichage
    semifinal1_result = None
    semifinal2_result = None
    final_result = None

    if tournament.semifinal1:
        semifinal1_result = GameResult.objects.filter(game=tournament.semifinal1).first()
    if tournament.semifinal2:
        semifinal2_result = GameResult.objects.filter(game=tournament.semifinal2).first()
    if tournament.final:
        final_result = GameResult.objects.filter(game=tournament.final).first()

    context = {
        'tournament': tournament,
        'semifinal1_result': semifinal1_result,
        'semifinal2_result': semifinal2_result,
        'final_result': final_result,
    }
    return render(request, 'game/tournament/detail_local_tournament.html', context)


def next_game_presentation_tournament(request, tournament_id, match_type):
    """
    Affiche un écran de 'préparation' pour la partie à venir (ex: semifinal1, semifinal2, final).
    Au bout de 3 sec, un bouton "Commencer la partie" apparaît.
    """
    tournament = get_object_or_404(LocalTournament, pk=tournament_id)

    if match_type == 'semifinal1':
        player_left = tournament.player1
        player_right = tournament.player2
    elif match_type == 'semifinal2':
        player_left = tournament.player3
        player_right = tournament.player4
    elif match_type == 'final':
        # Pour la finale, on suppose que les vainqueurs des 2 semi-finals sont déjà connus.
        # On peut aller chercher les winners via les GameResults:
        from .models import GameResult
        semi1_result = GameResult.objects.filter(game=tournament.semifinal1).first()
        semi2_result = GameResult.objects.filter(game=tournament.semifinal2).first()
        if semi1_result and semi2_result:
            # On récupère le pseudo vainqueur = "left" ou "right" correspond aux pseudos initiaux
            # ou stocker autrement. Ici on suppose qu'on a stocké direct "player1" ou "player2" dans winner.
            player_left = semi1_result.winner
            player_right = semi2_result.winner
        else:
            # Erreur ou fallback
            player_left = "????"
            player_right = "????"
    else:
        # Cas non géré
        return redirect('detail_local_tournament', tournament_id=tournament_id)

    context = {
        'tournament': tournament,
        'match_type': match_type,
        'player_left': player_left,
        'player_right': player_right,
    }
    return render(request, 'game/tournament/next_game_presentation_tournament.html', context)

# tournoi
def start_next_tournament_game(request, tournament_id, match_type):
    tournament = get_object_or_404(LocalTournament, pk=tournament_id)

    if match_type == 'semifinal1':
        # Créer systématiquement la GameSession pour la demi-finale 1
        gs = GameSession.objects.create(
            player_left=tournament.player1,
            player_right=tournament.player2,
            status='waiting'
        )

        # Associer des paramètres à cette GameSession
        if tournament.parameters:
            GameParameters.objects.create(
                game_session=gs,
                ball_speed=tournament.parameters.ball_speed,
                racket_size=tournament.parameters.racket_size,
                bonus_malus_activation=tournament.parameters.bonus_malus_activation,
                bumpers_activation=tournament.parameters.bumpers_activation
            )

        # Enregistrer cette demi-finale dans le tournoi
        tournament.semifinal1 = gs
        tournament.status = 'semifinal1_in_progress'
        tournament.save()

    elif match_type == 'semifinal2':
        # Créer la GameSession pour la demi-finale 2
        gs = GameSession.objects.create(
            player_left=tournament.player3,
            player_right=tournament.player4,
            status='waiting'
        )
        # Associer des paramètres à cette GameSession
        if tournament.parameters:
            GameParameters.objects.create(
                game_session=gs,
                ball_speed=tournament.parameters.ball_speed,
                racket_size=tournament.parameters.racket_size,
                bonus_malus_activation=tournament.parameters.bonus_malus_activation,
                bumpers_activation=tournament.parameters.bumpers_activation
            )
        tournament.semifinal2 = gs
        tournament.status = 'semifinal2_in_progress'
        tournament.save()

    elif match_type == 'final':
        # Pour la finale, on récupère éventuellement les vainqueurs
        semi1_result = GameResult.objects.filter(game=tournament.semifinal1).first()
        semi2_result = GameResult.objects.filter(game=tournament.semifinal2).first()

        # Récupérer les pseudos vainqueurs ou fallback
        winner_semifinal1 = semi1_result.winner if semi1_result else tournament.player1
        winner_semifinal2 = semi2_result.winner if semi2_result else tournament.player3

        # Créer la GameSession pour la finale
        gs = GameSession.objects.create(
            player_left=winner_semifinal1,
            player_right=winner_semifinal2,
            status='waiting'
        )
        # Associer des paramètres à la finale
        if tournament.parameters:
            GameParameters.objects.create(
                game_session=gs,
                ball_speed=tournament.parameters.ball_speed,
                racket_size=tournament.parameters.racket_size,
                bonus_malus_activation=tournament.parameters.bonus_malus_activation,
                bumpers_activation=tournament.parameters.bumpers_activation
            )
        tournament.final = gs
        tournament.status = 'final_in_progress'
        tournament.save()

    else:
        # Cas non géré (erreur ou retour)
        return redirect('detail_local_tournament', tournament_id=tournament.id)

    # Lance la loop asynchrone pour la partie
    schedule_game(str(gs.id))

    # Redirige vers la page de la partie
    return redirect('live_tournament_game', game_id=gs.id)

def live_tournament_game(request, game_id):
    """
    Affiche la page HTML (canvas + websocket) pour la partie <game_id>
    """
    return render(request, 'game/tournament/live_tournament_game.html', {'game_id': game_id})