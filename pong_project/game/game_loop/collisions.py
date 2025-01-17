# game/game_loop/collisions.py

import math
import time
from asgiref.sync import sync_to_async
from .redis_utils import set_key, get_key, delete_key
from .broadcast import notify_collision, notify_powerup_applied
from .powerups import apply_powerup

# Temps de cooldown pour les collisions avec les bumpers (en secondes)
COOLDOWN_TIME = 0.5

async def handle_paddle_collisions(game_id, paddle_left, paddle_right, ball):
    """
    Gère les collisions avec les paddles gauche et droite.
    Retourne 'score_left', 'score_right' ou None.
    """
    # Collision avec la raquette gauche
    if ball.x - ball.size <= paddle_left.x + paddle_left.width:
        if paddle_left.y <= ball.y <= paddle_left.y + paddle_left.height:
            ball.last_player = 'left'  # Mettre à jour le dernier joueur
            await handle_paddle_collision(game_id, 'left', paddle_left, ball)
            return None
        else:
            return 'score_right'

    # Collision avec la raquette droite
    if ball.x + ball.size >= paddle_right.x:
        if paddle_right.y <= ball.y <= paddle_right.y + paddle_right.height:
            ball.last_player = 'right'  # Mettre à jour le dernier joueur
            await handle_paddle_collision(game_id, 'right', paddle_right, ball)
            return None
        else:
            return 'score_left'

    return None

async def handle_paddle_collision(game_id, paddle_side, paddle, ball):
    """
    Gère la logique de collision entre la balle et une raquette.
    Ajuste la vitesse et la direction de la balle, met à jour Redis et notifie les clients.
    """
    relative_y = (ball.y - (paddle.y + paddle.height / 2)) / (paddle.height / 2)
    relative_y = max(-1, min(1, relative_y))  # Limiter à l'intervalle [-1, 1]

    angle = relative_y * (math.pi / 4)  # Max 45 degrés
    speed = math.hypot(ball.speed_x, ball.speed_y) * 1.03  # Augmenter la vitesse

    if paddle_side == 'left':
        ball.speed_x = speed * math.cos(angle)
    else:
        ball.speed_x = -speed * math.cos(angle)

    ball.speed_y = speed * math.sin(angle)

    # Mettre à jour la balle dans Redis
    await sync_to_async(set_key)(game_id, "ball_vx", ball.speed_x)
    await sync_to_async(set_key)(game_id, "ball_vy", ball.speed_y)

    # Notifier la collision via WebSocket
    collision_info = {
        'type': 'paddle_collision',
        'paddle_side': paddle_side,
        'new_speed_x': ball.speed_x,
        'new_speed_y': ball.speed_y,
    }
    await notify_collision(game_id, collision_info)

    print(f"[collisions.py] Ball collided with {paddle_side} paddle. New speed: ({ball.speed_x}, {ball.speed_y})")


def handle_border_collisions(ball):
    """
    Gère les collisions avec les bords supérieur et inférieur.
    Ajuste la vitesse de la balle en conséquence.
    """
    if ball.y - ball.size <= 50:
        ball.speed_y = abs(ball.speed_y)  # Rebond vers le bas
    elif ball.y + ball.size >= 350:
        ball.speed_y = -abs(ball.speed_y)  # Rebond vers le haut


async def handle_bumper_collision(game_id, ball, bumpers):
    """
    Gère les collisions entre la balle et les bumpers.
    Ajuste la vitesse et la direction de la balle, met à jour Redis et notifie les clients.
    """
    current_time = time.time()
    for bumper in bumpers:
        if bumper.active:
            dist = math.hypot(ball.x - bumper.x, ball.y - bumper.y)
            if dist <= ball.size + bumper.size:
                if current_time - bumper.last_collision_time >= COOLDOWN_TIME:
                    angle = math.atan2(ball.y - bumper.y, ball.x - bumper.x)
                    speed = math.hypot(ball.speed_x, ball.speed_y) * 1.05  # Augmentation de la vitesse
                    ball.speed_x = speed * math.cos(angle)
                    ball.speed_y = speed * math.sin(angle)

                    # Mettre à jour la balle dans Redis
                    await sync_to_async(set_key)(game_id, "ball_x", ball.x)
                    await sync_to_async(set_key)(game_id, "ball_y", ball.y)
                    await sync_to_async(set_key)(game_id, "ball_vx", ball.speed_x)
                    await sync_to_async(set_key)(game_id, "ball_vy", ball.speed_y)

                    # Mettre à jour le temps de la dernière collision
                    bumper.last_collision_time = current_time

                    # Notifier la collision via WebSocket
                    collision_info = {
                        'type': 'bumper_collision',
                        'bumper_x': bumper.x,
                        'bumper_y': bumper.y,
                        'new_speed_x': ball.speed_x,
                        'new_speed_y': ball.speed_y,
                    }
                    await notify_collision(game_id, collision_info)

                    print(f"[collisions.py] Ball collided with bumper at ({bumper.x}, {bumper.y}). New speed: ({ball.speed_x}, {ball.speed_y})")



async def handle_powerup_collision(game_id, ball, powerup_orbs):
    """
    Vérifie si la balle a ramassé un power-up en dehors des collisions avec les paddles.
    Applique l'effet du power-up au joueur concerné, met à jour Redis et notifie les clients.
    """
    for powerup_orb in powerup_orbs:
        if powerup_orb.active:
            dist = math.hypot(ball.x - powerup_orb.x, ball.y - powerup_orb.y)
            if dist <= ball.size + powerup_orb.size:
                # Associer le power-up au dernier joueur qui a touché la balle
                last_player = ball.last_player
                if last_player:
                    await apply_powerup(game_id, last_player, powerup_orb)
                    powerup_orb.deactivate()
                    await sync_to_async(delete_key)(game_id, f"powerup_{powerup_orb.effect_type}_active")
                    await sync_to_async(delete_key)(game_id, f"powerup_{powerup_orb.effect_type}_x")
                    await sync_to_async(delete_key)(game_id, f"powerup_{powerup_orb.effect_type}_y")
                    await notify_powerup_applied(game_id, last_player, powerup_orb.effect_type)
                    print(f"[collisions.py] Player {last_player} collected power-up {powerup_orb.effect_type} at ({powerup_orb.x}, {powerup_orb.y})")
                else:
                    # Si aucun joueur n'a touché la balle récemment, attribuer au joueur gauche par défaut
                    await apply_powerup(game_id, 'left', powerup_orb)
                    powerup_orb.deactivate()
                    await sync_to_async(delete_key)(game_id, f"powerup_{powerup_orb.effect_type}_active")
                    await sync_to_async(delete_key)(game_id, f"powerup_{powerup_orb.effect_type}_x")
                    await sync_to_async(delete_key)(game_id, f"powerup_{powerup_orb.effect_type}_y")
                    await notify_powerup_applied(game_id, 'left', powerup_orb.effect_type)
                    print(f"[collisions.py] Player left collected power-up {powerup_orb.effect_type} at ({powerup_orb.x}, {powerup_orb.y}) by default")
