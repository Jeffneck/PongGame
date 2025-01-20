# game/game_loop/game_objects_utils.py

import time
from .redis_microutils import get_key
from .dimensions_utils import get_terrain_rect
from .redis_macroutils import delete_powerup_redis, delete_bumper_redis
from ..game_objects import Paddle, Ball, PowerUpOrb, Bumper

FIELD_HEIGHT = 400

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

# -------------- PADDLES --------------------
async def move_paddles(game_id, paddle_left, paddle_right):
    left_vel = float(get_key(game_id, "paddle_left_velocity") or 0)
    right_vel = float(get_key(game_id, "paddle_right_velocity") or 0)

    # Appliquer la vélocité
    paddle_left.y += left_vel
    paddle_right.y += right_vel

    # Contraindre le mouvement dans [50, 350 - paddle.height]
    paddle_left.y = max(paddle_left.height, min(FIELD_HEIGHT - paddle_left.height, paddle_left.y))
    paddle_right.y = max(paddle_right.height, min(FIELD_HEIGHT - paddle_right.height, paddle_right.y))




# -------------- POWER UPS --------------------
async def count_active_powerups(game_id, powerup_orbs):
    count = 0
    for powerup_orb in powerup_orbs:
        active = get_key(game_id, f"powerup_{powerup_orb.effect_type}_active")
        if active and active.decode('utf-8') == '1':
            count += 1
    print(f"[loop.py] count_active_powerups ({count})")
    return count

async def handle_powerup_expiration(game_id, powerup_orbs):
    current_time = time.time()
    for powerup_orb in powerup_orbs:
        if powerup_orb.active and current_time - powerup_orb.spawn_time >= powerup_orb.duration:
            delete_powerup_redis(game_id, powerup_orb)
            print(f"[game_loop.py] PowerUp {powerup_orb.effect_type} expired at ({powerup_orb.x}, {powerup_orb.y})")


# -------------- BUMPERS --------------------
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
        active = get_key(game_id, f"bumper_{bumper.x}_{bumper.y}_active")
        active = get_key(game_id, f"bumper_{bumper.x}_{bumper.y}_")
        if active and active.decode('utf-8') == '1'and current_time - bumper.spawn_time >= bumper.duration:
            delete_bumper_redis(game_id, bumper)
            print(f"[loop.py] Bumper at ({bumper.x}, {bumper.y}) expired")