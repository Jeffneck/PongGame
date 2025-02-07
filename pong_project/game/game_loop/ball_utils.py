# game/game_loop/ball_utils.py
from .redis_utils import get_key, set_key, delete_key
from .dimensions_utils import get_terrain_rect
import time
import math
import random
import asyncio
from game.tasks import register_subtask

BALL_MIN_SPEED = 1
BALL_MAX_SPEED = 20
# -------------- BALL : UPDATE OBJECTS  --------------------
def move_ball(game_id, ball):
    ball.x = float(get_key(game_id, "ball_x")) + float(get_key(game_id, "ball_vx"))
    ball.y = float(get_key(game_id, "ball_y")) + float(get_key(game_id, "ball_vy"))
    update_ball_redis(game_id, ball)


def reset_ball(game_id, ball):
    terrain_rect = get_terrain_rect(game_id)
    center_x = terrain_rect['left'] + terrain_rect['width'] // 2
    center_y = terrain_rect['top'] + terrain_rect['height'] // 2

    # Get the initial ball speed multiplier from Redis / added
    speed_multiplier = int(get_key(game_id, "initial_ball_speed_multiplier"))
    initial_speed_x = random.choice([-1, 1]) * speed_multiplier  # Base speed * multiplier / modified
    initial_speed_y = random.choice([-1, 1]) * speed_multiplier

    ball.reset(center_x, center_y, initial_speed_x, initial_speed_y) #modified
    update_ball_redis(game_id, ball)

    print(f"[game_loop.py] Ball reset to ({ball.x}, {ball.y}) with speed ({ball.speed_x}, {ball.speed_y})")

# def reset_ball(game_id, ball):
#     terrain_rect = get_terrain_rect(game_id)
#     center_x = terrain_rect['left'] + terrain_rect['width'] // 2
#     center_y = terrain_rect['top'] + terrain_rect['height'] // 2

#     # 1. Mettre la balle au centre, vitesse 0
#     ball.reset(center_x, center_y, 0, 0)
#     update_ball_redis(game_id, ball)
#     print(f"[game_loop.py] Ball reset to ({ball.x}, {ball.y}) with speed (0, 0)")

#     # 2. Stocker en Redis un flag "waiting_for_launch"
#     #    et l'horodatage "reset_start_time"
#     set_key(game_id, "ball_is_waiting", 1)
#     set_key(game_id, "ball_reset_start_time", time.time())

# def launch_ball_after_score(game_id, ball):
#     wait_flag = get_key(game_id, "ball_is_waiting")
#     if wait_flag and wait_flag.decode('utf-8') == '1':
#         reset_start = float(get_key(game_id, "ball_reset_start_time") or 0)
#         # Si 1 seconde est écoulée
#         if time.time() - reset_start >= 1.0:
#             # -> On assigne la nouvelle vitesse
#             speed_multiplier = float(get_key(game_id, "initial_ball_speed_multiplier") or 1.0)
#             initial_speed_x = random.choice([-3, 3]) * speed_multiplier
#             initial_speed_y = random.choice([-3, 3]) * speed_multiplier
#             ball.speed_x = initial_speed_x
#             ball.speed_y = initial_speed_y
#             update_ball_redis(game_id, ball)
#             print(f"[game_loop.py] Ball started with speed ({ball.speed_x}, {ball.speed_y})")

#             # On supprime le flag
#             delete_key(game_id, "ball_is_waiting")
#             delete_key(game_id, "ball_reset_start_time")

# def reset_ball(game_id, ball):
#     terrain_rect = get_terrain_rect(game_id)
#     center_x = terrain_rect['left'] + terrain_rect['width'] // 2
#     center_y = terrain_rect['top'] + terrain_rect['height'] // 2
#     # Réinitialiser la balle en position centrale avec vitesse nulle
#     ball.reset(center_x, center_y, 0, 0)
#     update_ball_redis(game_id, ball)
#     print(f"[game_loop.py] Ball reset to ({ball.x}, {ball.y}) with speed (0, 0)")
#     # Lancer une tâche asynchrone qui, après 1 seconde, démarre la balle
#     # Lancer une tâche asynchrone qui, après 1 seconde, démarre la balle
#     # subtask = asyncio.create_task(start_ball_after_delay(game_id, ball))
#     # register_subtask(game_id, subtask) 
#     start_ball_after_delay(game_id, ball)#test
    
# async def start_ball_after_delay(game_id, ball):
#     """
#     Coroutine asynchrone qui attend 1s avant de démarrer la balle.
#     On gère CancelledError pour sortir proprement si le jeu est stoppé avant.
#     """
#     try:
#         await asyncio.sleep(1)
#     except asyncio.CancelledError:
#         print(f"[start_ball_after_delay] => CANCELLED for game_id={game_id}")
#         return

#     # Ici, vous pouvez définir les vitesses de départ souhaitées
#     speed_multiplier = float(get_key(game_id, "initial_ball_speed_multiplier") or 1.0)
#     initial_speed_x = random.choice([-3, 3]) * speed_multiplier
#     initial_speed_y = random.choice([-3, 3]) * speed_multiplier
#     ball.speed_x = initial_speed_x
#     ball.speed_y = initial_speed_y
#     update_ball_redis(game_id, ball)
#     print(f"[game_loop.py] Ball started with speed ({ball.speed_x}, {ball.speed_y})")

def move_ball_sticky(game_id, paddle_left, paddle_right, ball):
    stuck_side = get_key(game_id, "ball_stuck_side").decode('utf-8')  # 'left' ou 'right'
    
    # Récupérer la raquette correspondante
    if stuck_side == 'left':
        current_paddle = paddle_left
    else:
        current_paddle = paddle_right

    # Calculer y en fonction de sticky_relative_pos_<side>
    rel_pos = float(get_key(game_id, f"sticky_relative_pos_{stuck_side}") or 0)

    # Mettre la balle à la nouvelle position
    # X = collée contre la raquette
    if stuck_side == 'left':
        ball.x = current_paddle.x + current_paddle.width + ball.size
    else:
        ball.x = current_paddle.x - ball.size

    # Y = (paddle.y + rel_pos)
    ball.y = current_paddle.y + rel_pos

    # Vérifier si on doit la relâcher (ex: après 1s)
    start_t = float(get_key(game_id, f"sticky_start_time_{stuck_side}") or 0)
    if time.time() - start_t >= 1.0:
        # Relâcher la balle avec un petit boost
        release_ball_sticky(game_id, current_paddle, stuck_side, ball)



# -------------- BALL : UPDATE REDIS KEYS  --------------------
def stick_ball_to_paddle(game_id, stuck_side, current_paddle, ball):
    """
    Colle la balle sur la raquette <stuck_side>.
    """
    print(f"[sticky] stick ball to {stuck_side} paddle")
    # Calcul de la position relative
    relative_pos = ball.y - current_paddle.y

    # Stocker la vitesse originale de la balle pour la remettre plus tard (facultatif)
    set_key(game_id, "ball_original_vx", ball.speed_x)
    set_key(game_id, "ball_original_vy", ball.speed_y)

    # Indiquer en Redis que la balle est collée à cette raquette
    set_key(game_id, "ball_stuck", 1)
    set_key(game_id, "ball_stuck_side", stuck_side)
    set_key(game_id, f"sticky_relative_pos_{stuck_side}", relative_pos)
    set_key(game_id, f"sticky_start_time_{stuck_side}", time.time())

    # Mettre la balle immobile
    ball.speed_x = 0
    ball.speed_y = 0

    # Positionner la balle contre la raquette
    if stuck_side == 'left':
        ball.x = current_paddle.x + current_paddle.width + ball.size
    else:
        ball.x = current_paddle.x - ball.size

def release_ball_sticky(game_id, current_paddle, stuck_side, ball):
    print(f"[sticky] Releasing ball from {stuck_side} paddle")
    # on conserve l'ancienne

    # On récupère la vitesse originale (si on l'avait stockée)
    ball.speed_x = float(get_key(game_id, "ball_original_vx") or BALL_MIN_SPEED)
    ball.speed_y = float(get_key(game_id, "ball_original_vy") or BALL_MIN_SPEED)

    # on donne le status speed boosted pour la rendre plus rapide lors de la prochaine collision avec le paddle
    set_key(game_id, "ball_speed_boosted", 1)
    # manage_ball_speed_and_angle(game_id, current_paddle, stuck_side, ball)

    # Nettoyage des cles ayant permis a la balle de stuck
    delete_key(game_id, "ball_stuck")
    delete_key(game_id, "ball_stuck_side")
    delete_key(game_id, f"sticky_relative_pos_{stuck_side}")
    delete_key(game_id, f"sticky_start_time_{stuck_side}")
    delete_key(game_id, "ball_original_vx")
    delete_key(game_id, "ball_original_vy")

    # Nettoyer le flag sticky de la raquette
    delete_key(game_id, f"paddle_{stuck_side}_sticky")

# -------------- BALL : UPDATE REDIS GENERAL KEYS --------------------

def manage_ball_speed_and_angle(game_id, current_paddle, paddle_side, ball):
    
    ball_already_boosted = get_key(game_id, "ball_speed_already_boosted")
    ball_speed_boosted = get_key(game_id, "ball_speed_boosted")
    if ball_already_boosted and ball_already_boosted.decode('utf-8') == '1':
        ball.speed_x = float(get_key(game_id, "ball_speed_x_before_boost") or BALL_MIN_SPEED)
        ball.speed_y = float(get_key(game_id, "ball_speed_y_before_boost") or BALL_MIN_SPEED)
        delete_key(game_id, "ball_speed_x_before_boost")
        delete_key(game_id, "ball_speed_y_before_boost")
        delete_key(game_id, "ball_speed_already_boosted")
    
    if ball_speed_boosted and ball_speed_boosted.decode('utf-8') == '1':
        set_key(game_id, "ball_speed_x_before_boost", ball.speed_x)
        set_key(game_id, "ball_speed_y_before_boost", ball.speed_y)
        set_key(game_id, "ball_speed_already_boosted", 1)
        delete_key(game_id, "ball_speed_boosted")
        tmp_speed = math.hypot(ball.speed_x, ball.speed_y) * 2
    else :
        tmp_speed = math.hypot(ball.speed_x, ball.speed_y) + 0.3
    
    #calculer la vitesse de renvoi de la balle
    new_speed = max(BALL_MIN_SPEED, min(BALL_MAX_SPEED, tmp_speed)) 

    # calculer l'angle de renvoi de la balle
    relative_y = (ball.y - (current_paddle.y + current_paddle.height / 2)) / (current_paddle.height / 2)
    relative_y = max(-1, min(1, relative_y))  # Limiter à l'intervalle [-1, 1]
    angle = relative_y * (math.pi / 4)  # Max 45 degrés

    # definir la speed_x et y grace à la vitesse generale et l'angle de renvoi calculé
    new_speed_x = new_speed * math.cos(angle)
    if paddle_side == 'left':
        ball.speed_x = new_speed_x
    else:
        ball.speed_x = -new_speed_x

    ball.speed_y = new_speed * math.sin(angle)



def update_ball_redis(game_id, ball):
    set_key(game_id, "ball_x", ball.x)
    set_key(game_id, "ball_y", ball.y)
    set_key(game_id, "ball_vx", ball.speed_x)
    set_key(game_id, "ball_vy", ball.speed_y)