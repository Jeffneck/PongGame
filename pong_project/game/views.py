# game/views.py

from django.shortcuts import render, redirect
from .models import GameSession, GameResult, GameParameters
from .manager import schedule_game
from .forms import GameParametersForm
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
