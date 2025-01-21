# game/game_loop/paddles_utils.py
from .redis_utils import get_key, set_key

FIELD_HEIGHT = 400

# -------------- PADDLES --------------------
def move_paddles(game_id, paddle_left, paddle_right):
    left_vel = float(get_key(game_id, "paddle_left_velocity") or 0)
    right_vel = float(get_key(game_id, "paddle_right_velocity") or 0)

    # Appliquer la vélocité
    paddle_left.y += left_vel
    paddle_right.y += right_vel

    # Contraindre le mouvement dans [50, 350 - paddle.height]
    paddle_left.y = max(paddle_left.height, min(FIELD_HEIGHT - paddle_left.height, paddle_left.y))
    paddle_right.y = max(paddle_right.height, min(FIELD_HEIGHT - paddle_right.height, paddle_right.y))

# -------------- PADDLES : UPDATE REDIS--------------------
def update_paddles_redis(game_id, paddle_left, paddle_right):
    set_key(game_id, "paddle_left_y", paddle_left.y)
    set_key(game_id, "paddle_right_y", paddle_right.y)