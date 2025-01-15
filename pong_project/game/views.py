# game/views.py

from django.shortcuts import render, redirect
from .models import GameSession, GameResult
from .manager import schedule_game
from django.conf import settings
import redis
import uuid

r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

def index(request):
    """
    Page d'accueil -> bouton pour créer une partie
    """
    return render(request, 'game/index.html')

def create_game(request):
    """
    Crée un GameSession (UUID), init Redis, lance la loop en non-bloquant
    """
    session = GameSession.objects.create(status='running') 
    game_id = str(session.id)

    # Init Redis
    r.set(f"{game_id}:score_left", 0)
    r.set(f"{game_id}:score_right", 0)
    r.set(f"{game_id}:paddle_left_y", 150)
    r.set(f"{game_id}:paddle_right_y", 150)
    r.set(f"{game_id}:ball_x", 300)
    r.set(f"{game_id}:ball_y", 200)
    r.set(f"{game_id}:ball_vx", 3)
    r.set(f"{game_id}:ball_vy", 2)

    print(f"[create_game] GameSession {game_id} created, status=running. Scheduling game_loop.")
    schedule_game(game_id)

    return redirect('game', game_id=game_id)

def game_page(request, game_id):
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
