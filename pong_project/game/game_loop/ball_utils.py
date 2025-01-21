# game/game_loop/ball_utils.py
from .redis_utils import get_key, set_key
from .dimensions_utils import get_terrain_rect

# -------------- BALL : UPDATE OBJECTS  --------------------
def move_ball(game_id, ball):
    ball.x = float(get_key(game_id, "ball_x")) + float(get_key(game_id, "ball_vx"))
    ball.y = float(get_key(game_id, "ball_y")) + float(get_key(game_id, "ball_vy"))


def reset_ball(game_id, ball):
    terrain_rect = get_terrain_rect(game_id)
    center_x = terrain_rect['left'] + terrain_rect['width'] // 2
    center_y = terrain_rect['top'] + terrain_rect['height'] // 2
    ball.reset(center_x, center_y, 4, 4)  # Vitesse X/Y à ajuster
    update_ball_redis(game_id, ball)
    print(f"[game_loop.py] Ball reset to ({ball.x}, {ball.y}) with speed ({ball.speed_x}, {ball.speed_y})")


# -------------- BALL : UPDATE REDIS --------------------
def update_ball_redis(game_id, ball):
    set_key(game_id, "ball_x", ball.x)
    set_key(game_id, "ball_y", ball.y)
    set_key(game_id, "ball_vx", ball.speed_x)
    set_key(game_id, "ball_vy", ball.speed_y)