from .redis_microutils import set_key, get_key, delete_key

async def initialize_redis(game_id, paddle_left, paddle_right, ball, powerup_orbs, bumpers):
    # Positions initiales des raquettes
    set_key(game_id, "paddle_left_y", paddle_left.y)
    set_key(game_id, "paddle_right_y", paddle_right.y)

    # Vélocités initiales des raquettes (0 => immobiles)
    set_key(game_id, "paddle_left_velocity", 0)
    set_key(game_id, "paddle_right_velocity", 0)

    # Balle
    set_key(game_id, "ball_x", ball.x)
    set_key(game_id, "ball_y", ball.y)
    set_key(game_id, "ball_vx", ball.speed_x)
    set_key(game_id, "ball_vy", ball.speed_y)

    # Power-ups
    for powerup_orb in powerup_orbs:
        delete_key(game_id, f"powerup_{powerup_orb.effect_type}_active")
        delete_key(game_id, f"powerup_{powerup_orb.effect_type}_x")
        delete_key(game_id, f"powerup_{powerup_orb.effect_type}_y")

    # Bumpers
    for bumper in bumpers:
        delete_key(game_id, f"bumper_{bumper.x}_{bumper.y}_active")
        delete_key(game_id, f"bumper_{bumper.x}_{bumper.y}_x")
        delete_key(game_id, f"bumper_{bumper.x}_{bumper.y}_y")

async def update_paddles_redis(game_id, paddle_left, paddle_right):
    left_vel = float(get_key(game_id, "paddle_left_velocity") or 0)
    right_vel = float(get_key(game_id, "paddle_right_velocity") or 0)

    # Appliquer la vélocité
    paddle_left.y += left_vel
    paddle_right.y += right_vel

    # Contraindre le mouvement dans [50, 350 - paddle.height]
    paddle_left.y = max(50, min(350 - paddle_left.height, paddle_left.y))
    paddle_right.y = max(50, min(350 - paddle_right.height, paddle_right.y))

    # Stocker la position mise à jour
    set_key(game_id, "paddle_left_y", paddle_left.y)
    set_key(game_id, "paddle_right_y", paddle_right.y)

async def update_paddles_redis(game_id, paddle_left, paddle_right):
    set_key(game_id, "paddle_left_y", paddle_left.y)
    set_key(game_id, "paddle_right_y", paddle_right.y)


async def update_ball_redis(game_id, ball):
    set_key(game_id, "ball_x", ball.x)
    set_key(game_id, "ball_y", ball.y)
    set_key(game_id, "ball_vx", ball.speed_x)
    set_key(game_id, "ball_vy", ball.speed_y)

async def delete_powerup_redis(game_id, powerup_orb):
    powerup_orb.deactivate()
    delete_key(game_id, f"powerup_{powerup_orb.effect_type}_active")
    delete_key(game_id, f"powerup_{powerup_orb.effect_type}_x")
    delete_key(game_id, f"powerup_{powerup_orb.effect_type}_y")

async def delete_bumper_redis(game_id, bumper):
    bumper.deactivate()
    set_key(game_id, f"bumper_{bumper.x}_{bumper.y}_active", 0)

# async def isActive_bumper_redis(game_id, bumper):
#     active = get_key(game_id, f"bumper_{bumper.x}_{bumper.y}_active")
#     return (active and active.decode('utf-8') == '1')

# async def isExpirated_bumper_redis(game_id, bumper):


# async def isActive_powerup_redis(game_id, powerup_orb):
#     active = get_key(game_id, f"powerup_{powerup_orb.effect_type}_active")
#     return (active and active.decode('utf-8') == '1')



# toutes les fonctions qui utilisent setkey/ get key / delete key
# mettre sync to async () ?