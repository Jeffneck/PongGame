# game/game_loop/loop.py

import asyncio
import time
from channels.layers import get_channel_layer
from ..models import GameSession, GameParameters, GameResult
from ..game_objects import Paddle, Ball, PowerUpOrb, Bumper
from .redis_utils import set_key, get_key, delete_key, scan_and_delete_keys
from .collisions import handle_paddle_collisions, handle_border_collisions, handle_bumper_collision, handle_powerup_collision
from .powerups import spawn_powerup, apply_powerup, handle_powerup_expiration
from .broadcast import broadcast_game_state
from asgiref.sync import sync_to_async
import random

FIELD_WIDTH = 800
FIELD_HEIGHT = 400
WIN_SCORE = 4
COOLDOWN_TIME = 0.5  # Secondes

async def initialize_game_objects(game_id, parameters):
    paddle_size = {1: 30, 2: 60, 3: 90}[parameters.racket_size]
    paddle_speed = 6  # Peut être ajusté si nécessaire
    ball_speed_multiplier = parameters.ball_speed

    # Obtenir les dimensions du terrain
    terrain_rect = await get_terrain_rect(game_id)

    # Initialiser les raquettes
    paddle_left = Paddle('left', paddle_size, paddle_speed)
    paddle_right = Paddle('right', paddle_size, paddle_speed)

    # Initialiser la balle
    initial_ball_speed_x = 4 * ball_speed_multiplier
    initial_ball_speed_y = 4 * ball_speed_multiplier
    ball = Ball(
        terrain_rect['left'] + terrain_rect['width'] // 2,
        terrain_rect['top'] + terrain_rect['height'] // 2,
        initial_ball_speed_x,
        initial_ball_speed_y
    )

    # Initialiser les power-ups et bumpers
    powerup_orbs = [
        PowerUpOrb(game_id, 'invert', terrain_rect, color=(255, 105, 180)),  # Rose pour inverser
        PowerUpOrb(game_id, 'shrink', terrain_rect, color=(255, 0, 0)),      # Rouge pour rétrécir
        PowerUpOrb(game_id, 'ice', terrain_rect, color=(0, 255, 255)),       # Cyan pour glace
        PowerUpOrb(game_id, 'speed', terrain_rect, color=(255, 215, 0)),     # Or pour vitesse
        PowerUpOrb(game_id, 'flash', terrain_rect, color=(255, 255, 0)),     # Jaune pour flash
        PowerUpOrb(game_id, 'sticky', terrain_rect, color=(50, 205, 50))     # Vert lime pour collant
    ]

    bumpers = []
    if parameters.bumpers_activation:
        bumpers = [Bumper(game_id, terrain_rect) for _ in range(3)]  # Ajuster le nombre si nécessaire

    return paddle_left, paddle_right, ball, powerup_orbs, bumpers

async def get_game_status(game_id):
    try:
        session = await sync_to_async(GameSession.objects.get)(pk=game_id)
        return session.status
    except GameSession.DoesNotExist:
        return 'finished'

async def get_game_parameters(game_id):
    try:
        session = await sync_to_async(GameSession.objects.get)(pk=game_id)
        parameters = await sync_to_async(getattr)(session, 'parameters', None)
        return parameters
    except GameSession.DoesNotExist:
        return None

async def initialize_redis(game_id, paddle_left, paddle_right, ball, powerup_orbs, bumpers):
    # Positions initiales des raquettes
    set_key(game_id, "paddle_left_y", paddle_left.y)
    set_key(game_id, "paddle_right_y", paddle_right.y)

    # Vélocités initiales des raquettes (0 => immobiles)
    set_key(game_id, "paddle_left_velocity", 0)
    set_key(game_id, "paddle_right_velocity", 0)

    # Balle
    set_key(game_id, "ball_x", ball.x)
    set_key(game_id, "ball_y", ball.y)
    set_key(game_id, "ball_vx", ball.speed_x)
    set_key(game_id, "ball_vy", ball.speed_y)

    # Power-ups
    for powerup_orb in powerup_orbs:
        delete_key(game_id, f"powerup_{powerup_orb.effect_type}_active")
        delete_key(game_id, f"powerup_{powerup_orb.effect_type}_x")
        delete_key(game_id, f"powerup_{powerup_orb.effect_type}_y")

    # Bumpers
    for bumper in bumpers:
        delete_key(game_id, f"bumper_{bumper.x}_{bumper.y}_active")
        delete_key(game_id, f"bumper_{bumper.x}_{bumper.y}_x")
        delete_key(game_id, f"bumper_{bumper.x}_{bumper.y}_y")

async def update_paddles_from_redis(game_id, paddle_left, paddle_right):
    left_vel = float(get_key(game_id, "paddle_left_velocity") or 0)
    right_vel = float(get_key(game_id, "paddle_right_velocity") or 0)

    # Appliquer la vélocité
    paddle_left.y += left_vel
    paddle_right.y += right_vel

    # Contraindre le mouvement dans [50, 350 - paddle.height]
    paddle_left.y = max(50, min(350 - paddle_left.height, paddle_left.y))
    paddle_right.y = max(50, min(350 - paddle_right.height, paddle_right.y))

    # Stocker la position mise à jour
    set_key(game_id, "paddle_left_y", paddle_left.y)
    set_key(game_id, "paddle_right_y", paddle_right.y)

async def update_ball_redis(game_id, ball):
    set_key(game_id, "ball_x", ball.x)
    set_key(game_id, "ball_y", ball.y)
    set_key(game_id, "ball_vx", ball.speed_x)
    set_key(game_id, "ball_vy", ball.speed_y)

async def check_collisions(game_id, paddle_left, paddle_right, ball, bumpers, powerup_orbs):
    # Gérer les collisions avec les raquettes
    collision = await handle_paddle_collisions(game_id, paddle_left, paddle_right, ball)
    if collision:
        return collision

    # Gérer les collisions avec les bords
    handle_border_collisions(ball)

    # Gérer les collisions avec les bumpers
    await handle_bumper_collision(game_id, ball, bumpers)

    # Gérer les collisions avec les power-ups
    await handle_powerup_collision(game_id, ball, powerup_orbs)

    return None

async def handle_score(game_id, scorer):
    if scorer == 'score_left':
        score_left = int(get_key(game_id, "score_left") or 0) + 1
        set_key(game_id, "score_left", score_left)
        print(f"[loop.py] Player Left scored. Score: {score_left} - {get_key(game_id, 'score_right')}")
        if score_left >= WIN_SCORE:
            await finish_game(game_id, 'left')
    elif scorer == 'score_right':
        score_right = int(get_key(game_id, "score_right") or 0) + 1
        set_key(game_id, "score_right", score_right)
        print(f"[loop.py] Player Right scored. Score: {get_key(game_id, 'score_left')} - {score_right}")
        if score_right >= WIN_SCORE:
            await finish_game(game_id, 'right')

async def finish_game(game_id, winner):
    print(f"[loop.py] Game {game_id} finished, winner={winner}")
    channel_layer = get_channel_layer()
    try:
        session = await sync_to_async(GameSession.objects.get)(pk=game_id)
        session.status = 'finished'
        await sync_to_async(session.save)()

        score_left = int(get_key(game_id, "score_left") or 0)
        score_right = int(get_key(game_id, "score_right") or 0)
        await sync_to_async(GameResult.objects.create)(
            game=session,
            winner=winner,
            score_left=score_left,
            score_right=score_right
        )
        print(f"[loop.py] GameResult created for game_id={game_id}, winner={winner}")
    except GameSession.DoesNotExist:
        print(f"[loop.py] GameSession {game_id} does not exist.")
        pass

    # Notifier
    await channel_layer.group_send(
        f"pong_{game_id}",
        {
            'type': 'game_over',
            'winner': winner
        }
    )

    # Nettoyer les clés Redis
    await scan_and_delete_keys(game_id)
    print(f"[loop.py] Redis keys deleted for game_id={game_id}")

async def spawn_bumper(game_id, bumper):
    terrain_rect = await get_terrain_rect(game_id)
    if await bumper.spawn(terrain_rect):
        set_key(game_id, f"bumper_{bumper.x}_{bumper.y}_active", 1)
        set_key(game_id, f"bumper_{bumper.x}_{bumper.y}_x", bumper.x)
        set_key(game_id, f"bumper_{bumper.x}_{bumper.y}_y", bumper.y)
        print(f"[loop.py] Bumper spawned at ({bumper.x}, {bumper.y})")
        return True
    return False

async def count_active_powerups(game_id, powerup_orbs):
    count = 0
    for powerup_orb in powerup_orbs:
        active = get_key(game_id, f"powerup_{powerup_orb.effect_type}_active")
        if active and active.decode('utf-8') == '1':
            count += 1
    print(f"[loop.py] count_active_powerups ({count})")
    return count

async def count_active_bumpers(game_id, bumpers):
    count = 0
    for bumper in bumpers:
        active = get_key(game_id, f"bumper_{bumper.x}_{bumper.y}_active")
        if active and active.decode('utf-8') == '1':
            count += 1
    print(f"[loop.py] count_active_bumpers ({count})")
    return count

async def handle_bumper_expiration(game_id, bumpers):
    current_time = time.time()
    for bumper in bumpers:
        if bumper.active and current_time - bumper.spawn_time >= bumper.duration:
            bumper.deactivate()
            set_key(game_id, f"bumper_{bumper.x}_{bumper.y}_active", 0)
            print(f"[loop.py] Bumper at ({bumper.x}, {bumper.y}) expired")

# Ajoutez d'autres fonctions nécessaires, en important depuis les modules respectifs.
