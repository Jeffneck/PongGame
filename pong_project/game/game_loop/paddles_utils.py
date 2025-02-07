# game/game_loop/paddles_utils.py
from .redis_utils import get_key, set_key
from .dimensions_utils import get_terrain_rect
# FIELD_HEIGHT = 400

# -------------- PADDLES --------------------
def move_paddles(game_id, paddle_left, paddle_right):
    # 1) Lire les infos depuis Redis
    left_vel = float(get_key(game_id, "paddle_left_velocity") or 0)
    right_vel = float(get_key(game_id, "paddle_right_velocity") or 0)

    # Get initial height for both paddles / added
    initial_height = float(get_key(game_id, "initial_paddle_height"))

    # Hauteurs
    new_left_height = float(get_key(game_id, "paddle_left_height") or initial_height)
    new_right_height = float(get_key(game_id, "paddle_right_height") or initial_height)

    # Effets
    is_left_inverted = bool(get_key(game_id, "paddle_left_inverted"))
    is_right_inverted = bool(get_key(game_id, "paddle_right_inverted"))
    is_left_on_ice = bool(get_key(game_id, "paddle_left_ice_effect"))
    is_right_on_ice = bool(get_key(game_id, "paddle_right_ice_effect"))
    has_left_speed_boost = bool(get_key(game_id, "paddle_left_speed_boost"))
    has_right_speed_boost = bool(get_key(game_id, "paddle_right_speed_boost"))

    # 2) Appliquer la hauteur
    paddle_left.height = new_left_height
    paddle_right.height = new_right_height

    # 3) Calculer la direction effective
    #    si invert => inverser le signe
    if is_left_inverted:
        left_vel = -left_vel
    if is_right_inverted:
        right_vel = -right_vel

    #    si speed_boost => multiplier la vitesse
    if has_left_speed_boost:
        left_vel *= 1.5
    if has_right_speed_boost:
        right_vel *= 1.5

    # 4) Déduire direction ou laisser en “velocity”
    #    si on préfère la “direction” => -1,0,+1
    #    ou rester en “velocity” direct
    #    Dans le Paddle, on a la logique : if is_on_ice => friction etc.
    direction_left = 0
    if left_vel > 0: direction_left = 1
    elif left_vel < 0: direction_left = -1

    direction_right = 0
    if right_vel > 0: direction_right = 1
    elif right_vel < 0: direction_right = -1

    # 5) Appeler la méthode move(...) de la classe Paddle
    terrain_top = 50
    terrain_bottom = 350

    # On peut éventuellement passer “speed_boost” dans la signature.
    # Ou, comme ci-dessous, vous appliquez la friction/glace directement dedans.
    paddle_left.move(direction_left, is_left_on_ice, terrain_top, terrain_bottom, speed_boost=has_left_speed_boost)
    paddle_right.move(direction_right, is_right_on_ice, terrain_top, terrain_bottom, speed_boost=has_right_speed_boost)

    # 6) Sauvegarder la position finale dans Redis
    set_key(game_id, "paddle_left_y", paddle_left.y)
    set_key(game_id, "paddle_right_y", paddle_right.y)
    # Ici, on peut aussi sauvegarder la velocity si on veut la persister.

# -------------- PADDLES : UPDATE REDIS--------------------
# def update_paddles_redis(game_id, paddle_left, paddle_right):
#     """Updates paddle positions considering active effects."""
#     left_vel = float(get_key(game_id, f"paddle_left_velocity") or 0)
#     right_vel = float(get_key(game_id, f"paddle_right_velocity") or 0)

#     # Apply speed boost if active
#     if get_key(game_id, f"paddle_left_speed_boost"):
#         left_vel *= 1.5  # 50% speed increase
#     if get_key(game_id, f"paddle_right_speed_boost"):
#         right_vel *= 1.5  # 50% speed increase

#     # Convert velocity to direction
#     left_direction = 0 if left_vel == 0 else (1 if left_vel > 0 else -1)
#     right_direction = 0 if right_vel == 0 else (1 if right_vel > 0 else -1)

#     # Apply inverted controls first
#     if get_key(game_id, f"paddle_left_inverted"):
#         left_direction *= -1
#         left_vel *= -1
#     if get_key(game_id, f"paddle_right_inverted"):
#         right_direction *= -1
#         right_vel *= -1

#     # Check ice effects
#     left_on_ice = bool(get_key(game_id, f"paddle_left_ice_effect"))
#     right_on_ice = bool(get_key(game_id, f"paddle_right_ice_effect"))

#     # Get current paddle heights from Redis
#     left_height = float(get_key(game_id, f"paddle_left_height") or paddle_left.height)
#     right_height = float(get_key(game_id, f"paddle_right_height") or paddle_right.height)

#     # Define boundaries
#     TOP_BOUNDARY = 50
#     BOTTOM_BOUNDARY = 350  # This is the bottom border of the play area

#     # Move paddles with ice physics if active, otherwise normal movement
#     if left_on_ice:
#         paddle_left.move(left_direction, left_on_ice, TOP_BOUNDARY, BOTTOM_BOUNDARY)
#     else:
#         # Update position
#         paddle_left.y += left_vel
#         # Constrain movement using current height
#         # Bottom boundary is the maximum y position where the paddle can be placed
#         paddle_left.y = max(TOP_BOUNDARY, min(BOTTOM_BOUNDARY - left_height, paddle_left.y))

#     if right_on_ice:
#         paddle_right.move(right_direction, right_on_ice, TOP_BOUNDARY, BOTTOM_BOUNDARY)
#     else:
#         # Update position
#         paddle_right.y += right_vel
#         # Constrain movement using current height
#         paddle_right.y = max(TOP_BOUNDARY, min(BOTTOM_BOUNDARY - right_height, paddle_right.y))
#     set_key(game_id, f"paddle_left_y", paddle_left.y)
#     set_key(game_id, f"paddle_right_y", paddle_right.y)