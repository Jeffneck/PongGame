# game/game_loop/ball_utils.py
from .redis_utils import get_key, set_key, delete_key
from .dimensions_utils import get_terrain_rect
import time
import math
import random

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
    speed_multiplier = float(get_key(game_id, "initial_ball_speed_multiplier"))
    initial_speed = 4 * speed_multiplier  # Base speed * multiplier

    ball.reset(center_x, center_y, initial_speed, initial_speed) #modified
    update_ball_redis(game_id, ball)
    print(f"[game_loop.py] Ball reset to ({ball.x}, {ball.y}) with speed ({ball.speed_x}, {ball.speed_y})")


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
        release_ball_sticky(game_id, stuck_side, ball)



# -------------- BALL : UPDATE REDIS KEYS  --------------------
def stick_ball_to_paddle(game_id, stuck_side, paddle, ball):
    """
    Colle la balle sur la raquette <stuck_side>.
    """
    print(f"[sticky] stick ball to {stuck_side} paddle")
    # Calcul de la position relative
    relative_pos = ball.y - paddle.y

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
        ball.x = paddle.x + paddle.width + ball.size
    else:
        ball.x = paddle.x - ball.size

def release_ball_sticky(game_id, stuck_side, ball):
    print(f"[sticky] Releasing ball from {stuck_side} paddle")

    # # On récupère la vitesse originale (si on l'avait stockée)
    # original_vx = float(get_key(game_id, "ball_original_vx") or 3)
    # original_vy = float(get_key(game_id, "ball_original_vy") or 0) / removed

    # Get the initial ball speed multiplier / added
    speed_multiplier = float(get_key(game_id, "initial_ball_speed_multiplier"))
    base_speed = 4 * speed_multiplier

    # # Petit boost
    # speed = math.hypot(original_vx, original_vy) / removed
    new_speed = base_speed * 1.3  # 30% de boost / modified

    # On choisit la direction en X selon le côté
    if stuck_side == 'left':
        ball.speed_x = +abs(new_speed)  # vers la droite
    else:
        ball.speed_x = -abs(new_speed)  # vers la gauche

    # On met un léger angle en Y pour éviter la ligne pure horizontale
    ball.speed_y = 0.3 * new_speed * random.choice([-1, 1])

    # Nettoyage
    delete_key(game_id, "ball_stuck")
    delete_key(game_id, "ball_stuck_side")
    delete_key(game_id, f"sticky_relative_pos_{stuck_side}")
    delete_key(game_id, f"sticky_start_time_{stuck_side}")
    delete_key(game_id, "ball_original_vx")
    delete_key(game_id, "ball_original_vy")

# -------------- BALL : UPDATE REDIS GENERAL KEYS --------------------
def update_ball_redis(game_id, ball):
    set_key(game_id, "ball_x", ball.x)
    set_key(game_id, "ball_y", ball.y)
    set_key(game_id, "ball_vx", ball.speed_x)
    set_key(game_id, "ball_vy", ball.speed_y)