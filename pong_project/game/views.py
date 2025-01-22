# game/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
import time
from .models import GameSession, GameResult, GameParameters, LocalTournament
from .manager import schedule_game
from .forms import GameParametersForm, LocalTournamentForm
from .game_loop.redis_utils import set_key
import redis
from django.conf import settings

r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

def index(request):
    """
    Page d'accueil -> bouton pour créer une partie
    """
    return render(request, 'game/index.html')

def create_game(request):
    """
    Crée un GameSession (UUID), init Redis avec les paramètres personnalisés, lance la loop en non-bloquant
    """
    if request.method == 'POST':
        form = GameParametersForm(request.POST)
        if form.is_valid():
            # Créer une nouvelle GameSession
            session = GameSession.objects.create(status='running') 
            game_id = str(session.id)

            # Créer les GameParameters liés à cette session
            parameters = form.save(commit=False)
            parameters.game_session = session
            parameters.save()

            # Initialiser Redis avec les paramètres personnalisés
            set_key(game_id, "score_left", 0)
            set_key(game_id, "score_right", 0)
            set_key(game_id, "paddle_left_y", 150)
            set_key(game_id, "paddle_right_y", 150)
            set_key(game_id, "ball_x", 300)
            set_key(game_id, "ball_y", 200)
            # Ajuster la vitesse de la balle selon le paramètre
            ball_vx = 2 * parameters.ball_speed
            ball_vy = 1 * parameters.ball_speed
            set_key(game_id, "ball_vx", ball_vx)
            set_key(game_id, "ball_vy", ball_vy)

            print(f"[create_game] GameSession {game_id} created avec paramètres personnalisés. Scheduling game_loop.")
            schedule_game(game_id)

            return redirect('game', game_id=game_id)
    else:
        form = GameParametersForm()

    return render(request, 'game/create_game.html', {'form': form})






def game(request, game_id):
    """
    Affiche la page HTML (canvas + websocket) pour la partie <game_id>
    """
    return render(request, 'game/game.html', {'game_id': game_id})

def list_results(request):
    """
    Affiche la liste des parties terminées.
    """
    results = GameResult.objects.select_related('game').order_by('-ended_at')[:20]
    return render(request, 'game/results.html', {'results': results})

def create_local_tournament(request):
    if request.method == 'POST':
        form = LocalTournamentForm(request.POST)
        if form.is_valid():
            tournament = form.save()
            # Ici, tu peux éventuellement créer tes 2 GameSession (demi-finales)
            # en fonction de player1/player2 vs player3/player4, etc.
            # Par exemple :
            
            game1 = GameSession.objects.create(
                player_left=tournament.player1,
                player_right=tournament.player2,
                status='running'
            )
            tournament.semifinal1 = game1
            game2 = GameSession.objects.create(
                player_left=tournament.player3,
                player_right=tournament.player4,
                status='running'
            )
            tournament.semifinal2 = game2
            
            tournament.save()
            
            # Ensuite, rediriger ou afficher la page du tournoi
            return redirect('detail_local_tournament', tournament_id=tournament.id)
    else:
        form = LocalTournamentForm()
    return render(request, 'game/create_local_tournament.html', {'form': form})



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
    return render(request, 'game/detail_local_tournament.html', context)


def prepare_game(request, tournament_id, match_type):
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
    return render(request, 'game/prepare_game.html', context)

# tournoi
def start_game(request, tournament_id, match_type):
    """
    Crée ou récupère la GameSession pour ce match, puis redirige vers la page du jeu.
    """
    tournament = get_object_or_404(LocalTournament, pk=tournament_id)

    if match_type == 'semifinal1':
        # si semifinal1 n'existe pas, on la crée
        if not tournament.semifinal1:
            gs = GameSession.objects.create(
                player_left=tournament.player1,
                player_right=tournament.player2,
                status='running'
            )
            tournament.semifinal1 = gs
            tournament.status = 'semifinal1_in_progress'
            tournament.save()
        else:
            gs = tournament.semifinal1

    elif match_type == 'semifinal2':
        if not tournament.semifinal2:
            gs = GameSession.objects.create(
                player_left=tournament.player3,
                player_right=tournament.player4,
                status='running'
            )
            tournament.semifinal2 = gs
            tournament.status = 'semifinal2_in_progress'
            tournament.save()
        else:
            gs = tournament.semifinal2

    elif match_type == 'final':
        if not tournament.final:
            # On va chercher les winners des 2 demi-finales
            from .models import GameResult
            semi1_result = GameResult.objects.filter(game=tournament.semifinal1).first()
            semi2_result = GameResult.objects.filter(game=tournament.semifinal2).first()
            if not semi1_result or not semi2_result:
                # Pas normal, on redirige
                return redirect('detail_local_tournament', tournament_id=tournament.id)

            gs = GameSession.objects.create(
                player_left=semi1_result.winner,
                player_right=semi2_result.winner,
                status='running'
            )
            tournament.final = gs
            tournament.status = 'final_in_progress'
            tournament.save()
        else:
            gs = tournament.final

    else:
        return redirect('detail_local_tournament', tournament_id=tournament.id)

    # Rediriger vers la page de la partie
    # Supposons que la vue s'appelle "live_game" et prend un param "game_id"
    return redirect('live_game', game_id=gs.id)