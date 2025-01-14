# game/game_loop.py
import asyncio
import time
import redis
from django.conf import settings

r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

TICK_RATE = 60  # 60 fps ?

async def game_loop():
    """
    Boucle principale asynchrone qui met à jour la balle ~60 fois par seconde
    """
    dt = 1 / TICK_RATE
    while True:
        update_ball()
        # broadcast aux clients WebSocket
        await broadcast_game_state()
        await asyncio.sleep(dt)

def update_ball():
    ball_x = float(r.get('ball_x') or 300)
    ball_y = float(r.get('ball_y') or 200)
    ball_vx = float(r.get('ball_vx') or 3)
    ball_vy = float(r.get('ball_vy') or 2)

    # Mettre à jour la position
    ball_x += ball_vx
    ball_y += ball_vy

    # Gérer rebonds sur le haut/bas (disons terrain H=400)
    if ball_y <= 0:
        ball_y = 0
        ball_vy = abs(ball_vy)
    elif ball_y >= 400:
        ball_y = 400
        ball_vy = -abs(ball_vy)

    # Gérer collisions avec raquettes (simplifié)
    # terrain W=600, raquette W=10, si balle arrive en x=0...
    # On lit paddle_left_y:
    paddle_left_y = float(r.get('paddle_left_y') or 150)
    # On teste si la balle est proche de x=10
    if ball_x <= 20:  # collision gauche
        # Vérifier la collision avec la raquette
        if paddle_left_y <= ball_y <= paddle_left_y + 60:
            # collision => rebond
            ball_x = 20
            ball_vx = abs(ball_vx)
        else:
            # but à gauche => score player right
            score_right = int(r.get('score_right') or 0) + 1
            r.set('score_right', score_right)
            # reset la balle
            ball_x = 300
            ball_y = 200
            ball_vx = 3
            ball_vy = 2

    # pareil pour la raquette de droite, x=580 environ
    paddle_right_y = float(r.get('paddle_right_y') or 150)
    if ball_x >= 580:
        # collision
        if paddle_right_y <= ball_y <= paddle_right_y + 60:
            ball_x = 580
            ball_vx = -abs(ball_vx)
        else:
            # but pour left
            score_left = int(r.get('score_left') or 0) + 1
            r.set('score_left', score_left)
            ball_x = 300
            ball_y = 200
            ball_vx = -3
            ball_vy = 2

    # stocker
    r.set('ball_x', ball_x)
    r.set('ball_y', ball_y)
    r.set('ball_vx', ball_vx)
    r.set('ball_vy', ball_vy)

async def broadcast_game_state():
    """
    Envoie l'état du jeu (ball, raquettes, scores) via le channel layer
    (pour que chaque client WebSocket reçoive l'update en temps réel).
    """
    from channels.layers import get_channel_layer
    channel_layer = get_channel_layer()
    # Récup state
    ball_x = float(r.get('ball_x') or 300)
    ball_y = float(r.get('ball_y') or 200)
    paddle_left_y = float(r.get('paddle_left_y') or 150)
    paddle_right_y = float(r.get('paddle_right_y') or 150)
    score_left = int(r.get('score_left') or 0)
    score_right = int(r.get('score_right') or 0)

    data = {
        'type': 'game_state',  # custom type
        'ball_x': ball_x,
        'ball_y': ball_y,
        'left': paddle_left_y,
        'right': paddle_right_y,
        'score_left': score_left,
        'score_right': score_right,
    }
    # group_send => envoi à tous les clients du groupe "pong_room"
    await channel_layer.group_send(
        'pong_room',  # nom du groupe
        {
            'type': 'broadcast_game_state',
            'data': data
        }
    )
