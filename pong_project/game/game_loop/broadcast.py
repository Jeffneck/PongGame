# game/game_loop/broadcast.py

from channels.layers import get_channel_layer

# --------- GAME STATE : NOTIFICATIONS -----------
async def broadcast_game_state(game_id, data):
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f"pong_{game_id}",
        {
            'type': 'broadcast_game_state',
            'data': data
        }
    )


# --------- POWER UPS : NOTIFICATIONS -----------
async def notify_powerup_spawned(game_id, powerup_orb):
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f"pong_{game_id}",
        {
            'type': 'powerup_spawned',
            'powerup': {
                'type': powerup_orb.effect_type,
                'x': powerup_orb.x,
                'y': powerup_orb.y,
                'color': list(powerup_orb.color)
            }
        }
    )

async def notify_powerup_applied(game_id, player, effect, channel_layer=None):
    if not channel_layer:
        channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f"pong_{game_id}",
        {
            'type': 'powerup_applied',
            'player': player,
            'effect': effect
        }
    )

async def notify_powerup_expired(game_id, powerup_orb):
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f"pong_{game_id}",
        {
            'type': 'powerup_expired',
            'powerup': {
                'type': powerup_orb.effect_type,
                'x': powerup_orb.x,
                'y': powerup_orb.y
            }
        }
    )

# --------- COLLISIONS : NOTIFICATIONS -----------
async def notify_collision(game_id, collision_info):
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f"pong_{game_id}",
        {
            'type': 'collision_event',
            'collision': collision_info
        }
    )

async def notify_paddle_collision(game_id, paddle_side, ball):
    collision_info = {
        'type': 'paddle_collision',
        'paddle_side': paddle_side,
        'new_speed_x': ball.speed_x,
        'new_speed_y': ball.speed_y,
    }
    await notify_collision(game_id, collision_info)

    print(f"[collisions.py] Ball collided with {paddle_side} paddle. New speed: ({ball.speed_x}, {ball.speed_y})")

async def notify_border_collision(game_id, border_side, ball):
    collision_info = {
        'type': 'border_collision',
        'border_side': border_side,
        'coor_x_collision': ball.x,
    }
    await notify_collision(game_id, collision_info)

    print(f"[collisions.py] Ball collided with {border_side} border at coor x = {ball}.")

async def notify_bumper_collision(game_id, bumper, ball):
    collision_info = {
        'type': 'bumper_collision',
        'bumper_x': bumper.x,
        'bumper_y': bumper.y,
        'new_speed_x': ball.speed_x,
        'new_speed_y': ball.speed_y,
    }
    await notify_collision(game_id, collision_info)

    print(f"[collisions.py] Ball collided with bumper at ({bumper.x}, {bumper.y}). New speed: ({ball.speed_x}, {ball.speed_y})")


# --------- END GAME : NOTIFICATIONS -----------

async def notify_game_finished(game_id, winner, looser):
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f"pong_{game_id}",
        {
            'type': 'game_over',
            'winner': winner,
            'looser': looser
        }
    )

