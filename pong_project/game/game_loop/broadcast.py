# game/game_loop/broadcast.py

from channels.layers import get_channel_layer

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

async def notify_collision(game_id, collision_info):
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f"pong_{game_id}",
        {
            'type': 'collision_event',
            'collision': collision_info
        }
    )

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

async def broadcast_game_state(game_id, data):
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f"pong_{game_id}",
        {
            'type': 'broadcast_game_state',
            'data': data
        }
    )
