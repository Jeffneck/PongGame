# game/game_loop/collisions.py

import math
import random
import time
from asgiref.sync import sync_to_async
from .ball_utils import update_ball_redis
from .redis_utils import get_key, set_key, delete_key
from .powerups_utils import apply_powerup
from .broadcast import notify_paddle_collision, notify_border_collision, notify_bumper_collision, notify_powerup_applied

# Temps de cooldown pour les collisions avec les bumpers (en secondes)
# COOLDOWN_TIME = 0.5

# async def check_collisions(game_id, paddle_left, paddle_right, ball, bumpers, powerup_orbs):
#     # Gérer les collisions avec les raquettes
#     scoring = await handle_scoring_or_paddle_collision(game_id, paddle_left, paddle_right, ball)
#     if scoring:
#         return scoring

#     # Gérer les collisions avec les bords
#     await handle_border_collisions(game_id, ball)

#     # Gérer les collisions avec les bumpers
#     await handle_bumper_collision(game_id, ball, bumpers)

#     # Gérer les collisions avec les power-ups
#     await handle_powerup_collision(game_id, ball, powerup_orbs)

#     return None

async def handle_scoring_or_paddle_collision(game_id, paddle_left, paddle_right, ball):
    """
    Gère les collisions avec les paddles gauche et droite.
    Retourne 'score_left', 'score_right' ou None.
    """
    # print("handle_scoring_or_paddle_collision")
    # is_sticky = await handle_sticky_paddle_collision(game_id, paddle_left, paddle_right, ball)
    # if(is_sticky):
    #     return None

    # Collision avec la raquette gauche
    if ball.x - ball.size <= paddle_left.x + paddle_left.width:
        if paddle_left.y <= ball.y <= paddle_left.y + paddle_left.height:
            ball.last_player = 'left'  # Mettre à jour le dernier joueur
            await process_paddle_collision(game_id, 'left', paddle_left, ball)
            return None
        else:
            return 'score_right'

    # Collision avec la raquette droite
    if ball.x + ball.size >= paddle_right.x:
        if paddle_right.y <= ball.y <= paddle_right.y + paddle_right.height:
            ball.last_player = 'right'  # Mettre à jour le dernier joueur
            await process_paddle_collision(game_id, 'right', paddle_right, ball)
            return None
        else:
            return 'score_left'

    return None

# async def handle_sticky_paddle_collision(game_id, paddle_left, paddle_right, ball):
    
#     print("handle_sticky_paddle_collision")
#     is_sticky = False
#     # check if ball is stuck to any paddle
#     left_stuck = get_key(game_id, f"ball_stuck_to_left")
#     right_stuck = get_key(game_id, f"ball_stuck_to_right")
#     ball_moved = False

#     left_stuck = get_key(game_id, f"ball_stuck_to_left")
#     right_stuck = get_key(game_id, f"ball_stuck_to_right")
#     ball_moved = False

#     if left_stuck or right_stuck:
#         is_sticky = True
#         stuck_side = 'left' if left_stuck else 'right'
#         sticky_start = float(get_key(game_id, f"sticky_start_{stuck_side}") or 0)
#         relative_pos = float(get_key(game_id, f"sticky_relative_pos_{stuck_side}") or 0)
#         current_paddle = paddle_left if stuck_side == 'left' else paddle_right
        
#         # Check if 1 second has passed
#         if time.time() - sticky_start >= 1.0:
#             # Get the original speed that was stored when the ball got stuck
#             original_speed_x = float(get_key(game_id, f"ball_original_speed_x") or ball.speed_x)
#             original_speed_y = float(get_key(game_id, f"ball_original_speed_y") or ball.speed_y)
            
#             # Calculate the original speed magnitude and boost it
#             original_speed = math.hypot(original_speed_x, original_speed_y)
#             new_speed = original_speed * 1.3
            
#             # Position the ball and set its velocity
#             if stuck_side == 'left':
#                 ball.x = paddle_left.x + paddle_left.width + ball.size
#                 ball.speed_x = new_speed  # Move right
#             else:
#                 ball.x = paddle_right.x - ball.size
#                 ball.speed_x = -new_speed  # Move left
            
#             # Add slight vertical component to prevent straight-line motion
#             ball.speed_y = new_speed * 0.2 * random.choice([-1, 1])
            
#             # Clean up Redis keys
#             delete_key(game_id, f"ball_stuck_to_{stuck_side}")
#             delete_key(game_id, f"sticky_start_{stuck_side}")
#             delete_key(game_id, f"sticky_relative_pos_{stuck_side}")
#             delete_key(game_id, f"ball_original_speed_x")
#             delete_key(game_id, f"ball_original_speed_y")
            
#             ball_moved = True
#         else:
#             # Update ball position to follow paddle
#             paddle_y = float(get_key(game_id, f"paddle_{stuck_side}_y") or current_paddle.y)
#             if stuck_side == 'left':
#                 ball.x = paddle_left.x + paddle_left.width + ball.size
#             else:
#                 ball.x = paddle_right.x - ball.size
#             ball.y = paddle_y + relative_pos
#             ball_moved = True
    
#     # IMPROVE tester sdans cette condition
#     if not ball_moved:
#         ball.move()
#     return (is_sticky)
#     #IMPROVE return is_sticky pour pouvoir gerer handle_score...


#ball
async def process_paddle_collision(game_id, paddle_side, paddle, ball):
    """
    Gère la logique de collision entre la balle et une raquette.
    Ajuste la vitesse et la direction de la balle, met à jour Redis et notifie les clients.
    """
    print("process_paddle_collision")

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
    update_ball_redis(game_id, ball)

    # Notifier la collision via WebSocket
    await notify_paddle_collision(game_id, paddle_side, ball)
    
# def make_paddle_sticky(game_id, paddle_side, paddle, ball):
#         print("make_paddle_sticky")
#         # Calculate relative position where ball hit the paddle
#         relative_pos = ball.y - paddle.y
        
#         if 0 <= relative_pos <= paddle.height:  # Only stick if within paddle bounds
#             # Store the original ball speed for later use
#             set_key(game_id, f"ball_original_speed_x", ball.speed_x)
#             set_key(game_id, f"ball_original_speed_y", ball.speed_y)
            
#             # Set sticky state in Redis
#             set_key(game_id, f"ball_stuck_to_{paddle_side}", 1)
#             set_key(game_id, f"sticky_start_{paddle_side}", time.time())
#             set_key(game_id, f"sticky_relative_pos_{paddle_side}", relative_pos)
            
#             # Stop the ball
#             ball.speed_x = 0
#             ball.speed_y = 0
            
#             # Position the ball exactly at the paddle
#             if paddle_side == 'left':
#                 ball.x = paddle.x + paddle.width + ball.size
#             else:
#                 ball.x = paddle.x - ball.size
#             ball.y = paddle.y + relative_pos


async def handle_border_collisions(game_id, ball):
    """
    Gère les collisions avec les bords supérieur et inférieur.
    Ajuste la vitesse de la balle en conséquence.
    """
    if ball.y - ball.size <= 50:
        border_side = "up"
        ball.speed_y = abs(ball.speed_y)  # Rebond vers le bas
        update_ball_redis(game_id, ball)
        await notify_border_collision(game_id, border_side, ball)

    elif ball.y + ball.size >= 350:
        border_side = "down"
        ball.speed_y = -abs(ball.speed_y)  # Rebond vers le haut
        update_ball_redis(game_id, ball)
        await notify_border_collision(game_id, border_side, ball)


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
                # if current_time - bumper.last_collision_time >= COOLDOWN_TIME:
                angle = math.atan2(ball.y - bumper.y, ball.x - bumper.x)
                speed = math.hypot(ball.speed_x, ball.speed_y) * 1.05  # Augmentation de la vitesse
                ball.speed_x = speed * math.cos(angle)
                ball.speed_y = speed * math.sin(angle)

                # Mettre à jour la balle dans Redis
                update_ball_redis(game_id, ball)

                # Mettre à jour le temps de la dernière collision
                bumper.last_collision_time = current_time

                # Notifier la collision via WebSocket
                await notify_bumper_collision(game_id, bumper, ball)
                    

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
