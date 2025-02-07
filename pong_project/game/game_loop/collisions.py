# game/game_loop/collisions.py

import math
import random
import time
from asgiref.sync import sync_to_async
from .ball_utils import  stick_ball_to_paddle, manage_ball_speed_and_angle, update_ball_redis
from .redis_utils import get_key, set_key, delete_key
from .powerups_utils import apply_powerup
from .broadcast import notify_paddle_collision, notify_border_collision, notify_bumper_collision, notify_powerup_applied

MIN_SPEED = 1.0

# async def handle_scoring_or_paddle_collision(game_id, paddle_left, paddle_right, ball):
#     """
#     Gère le fait qu'on marque un point ou qu'on ait juste un rebond sur la raquette.
#     Retourne 'score_left', 'score_right' ou None si on continue le jeu.
#     """
    
#     # 1) Vérifier si la balle sort à gauche => point pour la droite
#     if ball.x - ball.size <= paddle_left.x + paddle_left.width:
#     # if ball.x - ball.size  <= paddle_left.x:
#         # Soit on a collision, soit c'est un but
#         if paddle_left.y <= ball.y <= paddle_left.y + paddle_left.height:
#             # Collision raquette gauche
#             # Vérifier sticky
#             is_sticky = bool(get_key(game_id, "paddle_left_sticky") or 0)
#             if is_sticky : 
#                 is_already_stuck = bool(get_key(game_id, "ball_stuck") or 0)
#                 if not is_already_stuck:
#                     # On "colle" la balle
#                     stick_ball_to_paddle(game_id, 'left', paddle_left, ball)
#                     # set_key(game_id, "paddle_left_already_stuck", 1)
#                 return None
#             else:

#                 # Rebond classique
#                 ball.last_player = 'left'
#                 await process_paddle_collision(game_id, 'left', paddle_left, ball)
#                 return None
#         else:
#             # Balle sortie côté gauche => score pour la droite
#             return 'score_right'

#     # 2) Vérifier si la balle sort à droite => point pour la gauche
#     if ball.x + ball.size >= paddle_right.x - paddle_right.width :
#     # if ball.x  >= paddle_right.x:
#         if paddle_right.y <= ball.y <= paddle_right.y + paddle_right.height:
#             # Collision raquette droite
#             is_sticky = bool(get_key(game_id, "paddle_right_sticky") or 0)
#             if is_sticky:
#                 is_already_stuck = bool(get_key(game_id, "ball_stuck") or 0)
#                 if not is_already_stuck:
#                     # On "colle" la balle
#                     stick_ball_to_paddle(game_id, 'right', paddle_right, ball)
#                     # set_key(game_id, "paddle_right_already_stuck", 1)
#                 return None
#             else:
#                 ball.last_player = 'right'
#                 await process_paddle_collision(game_id, 'right', paddle_right, ball)
#                 return None
#         else:
#             return 'score_left'

#     return None

async def handle_scoring_or_paddle_collision(game_id, paddle_left, paddle_right, ball):
    """
    Gère le fait qu'on marque un point ou qu'on ait juste un rebond sur la raquette.
    Retourne 'score_left', 'score_right' ou None si on continue le jeu.
    """
    # 1) Vérifier si la balle est passée suffisamment pour être considérée comme un but
    # Ici, on utilise le centre de la balle (ball.x) pour déterminer le score.
    if ball.x + ball.size <= paddle_left.x + paddle_left.width and not (paddle_left.y <= ball.y <= paddle_left.y + paddle_left.height):
        return 'score_right'
    if ball.x - ball.size >= paddle_right.x - paddle_right.width and not (paddle_right.y <= ball.y <= paddle_right.y + paddle_right.height):
        return 'score_left'
    
    # 2) Vérifier la collision avec la raquette gauche
    # Ici, on détecte la collision dès que le bord gauche de la balle touche la raquette.
    if ball.speed_x < 0 and (ball.x - ball.size) <= (paddle_left.x + paddle_left.width):
        if paddle_left.y <= ball.y <= paddle_left.y + paddle_left.height:
            # Si la balle touche la raquette, réaligner la balle sur le bord de la raquette
            ball.x = paddle_left.x + paddle_left.width + ball.size
            await process_paddle_collision(game_id, 'left', paddle_left, ball)
            return None

    # 3) Vérifier la collision avec la raquette droite
    # Ici, on détecte la collision dès que le bord droit de la balle touche la raquette.
    if ball.speed_x > 0 and (ball.x + ball.size) >= (paddle_right.x - paddle_right.width):
        if paddle_right.y <= ball.y <= paddle_right.y + paddle_right.height:
            # Réaligner la balle sur le bord de la raquette
            ball.x = paddle_right.x - paddle_right.width - ball.size
            await process_paddle_collision(game_id, 'right', paddle_right, ball)
            return None

    return None

async def handle_scoring_or_paddle_collision(game_id, paddle_left, paddle_right, ball):
    """
    Gère le fait qu'on marque un point ou qu'on ait juste un rebond sur la raquette.
    (Prend en compte le "sticky".)
    Retourne 'score_left', 'score_right' ou None.
    """

    # 0) Si la balle est collée, on ignore la détection de but.
    is_stuck = bool(get_key(game_id, "ball_stuck") or 0)
    if is_stuck:
        return None

    # 1) Détection "balle passée à gauche => but pour la droite"
    if ball.x + ball.size <= paddle_left.x + paddle_left.width \
       and not (paddle_left.y <= ball.y <= paddle_left.y + paddle_left.height):
        return 'score_right'

    # 2) Détection "balle passée à droite => but pour la gauche"
    if ball.x - ball.size >= paddle_right.x - paddle_right.width \
       and not (paddle_right.y <= ball.y <= paddle_right.y + paddle_right.height):
        return 'score_left'
    
    # 3) Collision raquette gauche
    if ball.speed_x < 0 and (ball.x - ball.size) <= (paddle_left.x + paddle_left.width):
        if paddle_left.y <= ball.y <= paddle_left.y + paddle_left.height:
            # On aligne la balle sur le bord
            ball.x = paddle_left.x + paddle_left.width + ball.size
            is_sticky = bool(get_key(game_id, "paddle_left_sticky") or 0)
            if is_sticky : 
                is_already_stuck = bool(get_key(game_id, "ball_stuck") or 0)
                if not is_already_stuck:
                    # On "colle" la balle
                    stick_ball_to_paddle(game_id, 'left', paddle_left, ball)
                    set_key(game_id, "paddle_left_already_stuck", 1)
                return None
            else:
                ball.last_player = 'left'
                await process_paddle_collision(game_id, 'left', paddle_left, ball)
                return None

    # 4) Collision raquette droite
    if ball.speed_x > 0 and (ball.x + ball.size) >= (paddle_right.x - paddle_right.width):
        if paddle_right.y <= ball.y <= paddle_right.y + paddle_right.height:
            # On aligne la balle sur le bord
            ball.x = paddle_right.x - paddle_right.width - ball.size
            is_sticky = bool(get_key(game_id, "paddle_right_sticky") or 0)
            if is_sticky:
                is_already_stuck = bool(get_key(game_id, "ball_stuck") or 0)
                if not is_already_stuck:
                    # On "colle" la balle
                    stick_ball_to_paddle(game_id, 'right', paddle_right, ball)
                    set_key(game_id, "paddle_right_already_stuck", 1)
                return None
            else:
                ball.last_player = 'right'
                await process_paddle_collision(game_id, 'right', paddle_right, ball)
                return None

    return None


#ball
async def process_paddle_collision(game_id, paddle_side, current_paddle, ball):
    """
    Gère la logique de collision entre la balle et une raquette.
    Ajuste la vitesse et la direction de la balle, met à jour Redis et notifie les clients.
    """
    print("process_paddle_collision")

    ball.last_player = paddle_side 
    # speed = math.hypot(ball.speed_x, ball.speed_y) * 1.03  # Augmenter la vitesse
    manage_ball_speed_and_angle(game_id, current_paddle, paddle_side, ball)




    # Mettre à jour la balle dans Redis
    update_ball_redis(game_id, ball)

    # Notifier la collision via WebSocket
    await notify_paddle_collision(game_id, paddle_side, ball)
    

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
                speed = math.hypot(ball.speed_x, ball.speed_y)
                ball.speed_x = speed * math.cos(angle)
                ball.speed_y = speed * math.sin(angle)

                # Mettre à jour la balle dans Redis
                update_ball_redis(game_id, ball)

                # IMPROVE (inutile ?) Mettre à jour le temps de la dernière collision
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
