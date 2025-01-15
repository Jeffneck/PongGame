# game/game_loop.py

import redis
import asyncio
from django.conf import settings
from channels.layers import get_channel_layer
from .models import GameSession, GameResult
from asgiref.sync import sync_to_async

r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

FIELD_WIDTH = 600
FIELD_HEIGHT = 400
PADDLE_HEIGHT = 60
BALL_RADIUS = 7
WIN_SCORE = 2

async def game_loop(game_id):
    """
    Boucle principale pour UNE partie identifiée par game_id.
    Tourne ~60 fois/s tant que la partie est "running".
    """
    channel_layer = get_channel_layer()

    dt = 1/60
    print(f"[game_loop.py] Starting loop for game_id={game_id}.")
    while True:
        # Vérifier si la partie est encore "running"
        session_status = await get_game_status(game_id)
        if session_status != 'running':
            print(f"[game_loop.py] game_id={game_id} is not running (status={session_status}), break.")
            break

        update_ball(game_id)

        # Broadcast l'état
        await broadcast_game_state(game_id, channel_layer)

        # Checker si un joueur a gagné
        if check_game_finished(game_id):
            # On arrête
            await finish_game(game_id, channel_layer)
            print(f"[game_loop.py] game_id={game_id} finished (score reached). break.")
            break

        await asyncio.sleep(dt)

    print(f"[game_loop.py] game_id={game_id} loop ended.")

def update_ball(game_id):
    """Met à jour la balle pour la partie <game_id> (rebonds, collisions, etc.)."""
    ball_x_key = f"{game_id}:ball_x"
    ball_y_key = f"{game_id}:ball_y"
    vx_key = f"{game_id}:ball_vx"
    vy_key = f"{game_id}:ball_vy"

    ball_x = float(r.get(ball_x_key) or 300)
    ball_y = float(r.get(ball_y_key) or 200)
    vx = float(r.get(vx_key) or 3)
    vy = float(r.get(vy_key) or 2)

    # Positions raquettes
    left_y = float(r.get(f"{game_id}:paddle_left_y") or 150)
    right_y = float(r.get(f"{game_id}:paddle_right_y") or 150)

    # Scores
    score_left_key = f"{game_id}:score_left"
    score_right_key = f"{game_id}:score_right"
    score_left = int(r.get(score_left_key) or 0)
    score_right = int(r.get(score_right_key) or 0)

    # Move ball
    ball_x += vx
    ball_y += vy

    # Rebonds haut/bas
    if ball_y - BALL_RADIUS <= 0:
        ball_y = BALL_RADIUS
        vy = abs(vy)
    elif ball_y + BALL_RADIUS >= FIELD_HEIGHT:
        ball_y = FIELD_HEIGHT - BALL_RADIUS
        vy = -abs(vy)

    # Collision gauche
    if ball_x - BALL_RADIUS <= 20:  # ~ (x=10) + 10
        if left_y <= ball_y <= left_y + PADDLE_HEIGHT:
            # rebond
            ball_x = 20 + BALL_RADIUS
            vx = abs(vx)
            print(f"[game_loop.py] Ball collided with left paddle. New vx={vx}")
        else:
            # but pr right
            score_right += 1
            # reset
            ball_x = FIELD_WIDTH/2
            ball_y = FIELD_HEIGHT/2
            vx, vy = 3, 2
            print(f"[game_loop.py] Right player scored! score_right={score_right}")

    # Collision droite
    if ball_x + BALL_RADIUS >= FIELD_WIDTH - 20:
        if right_y <= ball_y <= right_y + PADDLE_HEIGHT:
            ball_x = FIELD_WIDTH - 20 - BALL_RADIUS
            vx = -abs(vx)
            print(f"[game_loop.py] Ball collided with right paddle. New vx={vx}")
        else:
            # but pr left
            score_left += 1
            ball_x = FIELD_WIDTH/2
            ball_y = FIELD_HEIGHT/2
            vx, vy = -3, 2
            print(f"[game_loop.py] Left player scored! score_left={score_left}")

    # Store
    r.set(ball_x_key, ball_x)
    r.set(ball_y_key, ball_y)
    r.set(vx_key, vx)
    r.set(vy_key, vy)
    r.set(score_left_key, score_left)
    r.set(score_right_key, score_right)

async def get_game_status(game_id):
    """
    Récupère le statut de la partie depuis la base de données.
    """
    try:
        session = await sync_to_async(GameSession.objects.get)(pk=game_id)
        return session.status
    except GameSession.DoesNotExist:
        return 'finished'

async def broadcast_game_state(game_id, channel_layer):
    """Envoie l'état à tous via group_send("pong_{game_id}", ...)."""
    group_name = f"pong_{game_id}"

    ball_x = float(r.get(f"{game_id}:ball_x") or 300)
    ball_y = float(r.get(f"{game_id}:ball_y") or 200)
    left_y = float(r.get(f"{game_id}:paddle_left_y") or 150)
    right_y = float(r.get(f"{game_id}:paddle_right_y") or 150)
    score_left = int(r.get(f"{game_id}:score_left") or 0)
    score_right = int(r.get(f"{game_id}:score_right") or 0)

    data = {
        'type': 'broadcast_game_state',
        'data': {
            'type': 'game_state',
            'ball_x': ball_x,
            'ball_y': ball_y,
            'left': left_y,
            'right': right_y,
            'score_left': score_left,
            'score_right': score_right,
        }
    }
    await channel_layer.group_send(group_name, data)
    print(f"[game_loop.py] Broadcast game_state for game_id={game_id}")

async def finish_game(game_id, channel_layer):
    """
    Met la session en 'finished', enregistre GameResult, notifie 'game_over', supprime les clés Redis...
    """
    from .models import GameSession, GameResult

    # Récup final
    score_left = int(r.get(f"{game_id}:score_left") or 0)
    score_right = int(r.get(f"{game_id}:score_right") or 0)
    winner = 'left' if score_left >= WIN_SCORE else 'right'

    # Mettre la session en finished
    try:
        session = await sync_to_async(GameSession.objects.get)(pk=game_id)
        session.status = 'finished'
        await sync_to_async(session.save)()

        # Créer un GameResult
        await sync_to_async(GameResult.objects.create)(
            game=session,
            winner=winner,
            score_left=score_left,
            score_right=score_right
        )
        print(f"[game_loop.py] GameResult created for game_id={game_id}, winner={winner}")
    except GameSession.DoesNotExist:
        print(f"[game_loop.py] GameSession {game_id} does not exist.")
        pass

    # Broadcast "game_over"
    await channel_layer.group_send(
        f"pong_{game_id}",
        {
            'type': 'game_over',
            'winner': winner
        }
    )
    print(f"[game_loop.py] Broadcast game_over for game_id={game_id}, winner={winner}")

    # Supprimer les clés Redis
    keys = list(r.scan_iter(f"{game_id}:*"))
    for key in keys:
        r.delete(key)
    print(f"[game_loop.py] Redis keys deleted for game_id={game_id}")

def check_game_finished(game_id):
    """
    Retourne True si un score >= WIN_SCORE
    """
    score_left = int(r.get(f"{game_id}:score_left") or 0)
    score_right = int(r.get(f"{game_id}:score_right") or 0)
    return (score_left >= WIN_SCORE) or (score_right >= WIN_SCORE)
