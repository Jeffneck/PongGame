# game/game_loop/paddles_utils.py
from .redis_utils import get_key, set_key
from .dimensions_utils import get_terrain_rect
# FIELD_HEIGHT = 400

# -------------- PADDLES --------------------
def move_paddles(game_id, paddle_left, paddle_right):
    left_vel = float(get_key(game_id, "paddle_left_velocity") or 0)
    right_vel = float(get_key(game_id, "paddle_right_velocity") or 0)

    terrain_rect = get_terrain_rect(game_id)
    terrain_top = terrain_rect['top']
    terrain_bottom = terrain_top + terrain_rect['height']

    # Appliquer la vélocité
    paddle_left.y += left_vel
    paddle_right.y += right_vel

    # Contraindre le mouvement dans les limites du terrain
    paddle_left.y = max(terrain_top, min(terrain_bottom - paddle_left.height, paddle_left.y))
    paddle_right.y = max(terrain_top, min(terrain_bottom - paddle_right.height, paddle_right.y))

# -------------- PADDLES : UPDATE REDIS--------------------
def update_paddles_redis(game_id, paddle_left, paddle_right):
    """Updates paddle positions considering active effects."""
    left_vel = float(get_key(game_id, f"paddle_left_velocity") or 0)
    right_vel = float(get_key(game_id, f"paddle_right_velocity") or 0)

    # Apply speed boost if active
    if get_key(game_id, f"paddle_left_speed_boost"):
        left_vel *= 1.5  # 50% speed increase
    if get_key(game_id, f"paddle_right_speed_boost"):
        right_vel *= 1.5  # 50% speed increase

    # Convert velocity to direction
    left_direction = 0 if left_vel == 0 else (1 if left_vel > 0 else -1)
    right_direction = 0 if right_vel == 0 else (1 if right_vel > 0 else -1)

    # Apply inverted controls first
    if get_key(game_id, f"paddle_left_inverted"):
        left_direction *= -1
        left_vel *= -1
    if get_key(game_id, f"paddle_right_inverted"):
        right_direction *= -1
        right_vel *= -1

    # Check ice effects
    left_on_ice = bool(get_key(game_id, f"paddle_left_ice_effect"))
    right_on_ice = bool(get_key(game_id, f"paddle_right_ice_effect"))

    # Get current paddle heights from Redis
    left_height = float(get_key(game_id, f"paddle_left_height") or paddle_left.height)
    right_height = float(get_key(game_id, f"paddle_right_height") or paddle_right.height)

    # Define boundaries
    TOP_BOUNDARY = 50
    BOTTOM_BOUNDARY = 350  # This is the bottom border of the play area

    # Move paddles with ice physics if active, otherwise normal movement
    if left_on_ice:
        paddle_left.move(left_direction, left_on_ice, TOP_BOUNDARY, BOTTOM_BOUNDARY)
    else:
        # Update position
        paddle_left.y += left_vel
        # Constrain movement using current height
        # Bottom boundary is the maximum y position where the paddle can be placed
        paddle_left.y = max(TOP_BOUNDARY, min(BOTTOM_BOUNDARY - left_height, paddle_left.y))

    if right_on_ice:
        paddle_right.move(right_direction, right_on_ice, TOP_BOUNDARY, BOTTOM_BOUNDARY)
    else:
        # Update position
        paddle_right.y += right_vel
        # Constrain movement using current height
        paddle_right.y = max(TOP_BOUNDARY, min(BOTTOM_BOUNDARY - right_height, paddle_right.y))
    set_key(game_id, f"paddle_left_y", paddle_left.y)
    set_key(game_id, f"paddle_right_y", paddle_right.y)