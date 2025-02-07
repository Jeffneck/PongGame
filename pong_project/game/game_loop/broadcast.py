# game/game_loop/broadcast.py

from channels.layers import get_channel_layer
from .redis_utils import get_key


# --------- GAME STATE : NOTIFICATIONS -----------
async def broadcast_game_state(game_id, channel_layer, paddle_left, paddle_right, ball, powerup_orbs, bumpers):
    """
    Envoie l'état actuel du jeu aux clients via WebSocket.
    """
    # Récupérer les états des power-ups
    powerups_data = []
    for powerup_orb in powerup_orbs:
        active = get_key(game_id, f"powerup_{powerup_orb.effect_type}_active" or 0)
        if active and active.decode('utf-8') == '1':
            x = float(get_key(game_id, f"powerup_{powerup_orb.effect_type}_x") or 0)
            y = float(get_key(game_id, f"powerup_{powerup_orb.effect_type}_y") or 0)
            powerups_data.append({
                'type': powerup_orb.effect_type,
                'x': x,
                'y': y,
                'color': list(powerup_orb.color)  # Convertir en liste pour JSON
            })

    # Récupérer les états des bumpers
    # print(f"[game_loop.py] bumpers to send: {bumpers}")
    bumpers_data = []
    for bumper in bumpers:
        active = get_key(game_id, f"bumper_{bumper.x}_{bumper.y}_active" or 0)
        if active and active.decode('utf-8') == '1':
            x = float(get_key(game_id, f"bumper_{bumper.x}_{bumper.y}_x") or 0)
            y = float(get_key(game_id, f"bumper_{bumper.x}_{bumper.y}_y") or 0)
            bumpers_data.append({
                'x': x,
                'y': y,
                'size': bumper.size,
                'color': list(bumper.color)  # Convertir en liste pour JSON
            })

    data = {
        'type': 'game_state',
        'ball_x': ball.x,
        'ball_y': ball.y,
        'ball_size': ball.size,
        'ball_speed_x': ball.speed_x,
        'ball_speed_y': ball.speed_y,
        'paddle_left_y': paddle_left.y,
        'paddle_right_y': paddle_right.y,
        'paddle_width': paddle_left.width,
        'paddle_left_height': paddle_left.height,
        'paddle_right_height': paddle_right.height,
        'score_left': int(get_key(game_id, "score_left") or 0),
        'score_right': int(get_key(game_id, "score_right") or 0),
        'powerups': powerups_data,
        'bumpers': bumpers_data,
        'flash_effect': bool(get_key(game_id, f"flash_effect"))
    }
    # IMPROVE le flash effect peut etre renvoye en notif powerup applied

    await channel_layer.group_send(f"pong_{game_id}", {
        'type': 'broadcast_game_state',
        'data': data
    })
    # print(f"[game_loop.py] Broadcast game_state for game_id={game_id}")




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

async def notify_countdown(game_id, countdown_nb):
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f"pong_{game_id}",
        {
            'type': 'countdown',
            'countdown_nb': countdown_nb
        }
    )

async def notify_scored(game_id):
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f"pong_{game_id}",
        {
            'type': 'scored',
            'scoreMsg': 'GOAL'
        }
    )


async def notify_powerup_applied(game_id, player, effect, effect_duration):
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f"pong_{game_id}",
        {
            'type': 'powerup_applied',
            'player': player,
            'effect': effect,
            'duration': effect_duration
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

# --------- BUMPERS : NOTIFICATIONS -----------
async def notify_bumper_spawned(game_id, bumper):
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f"pong_{game_id}",
        {
            'type': 'bumper_spawned',
            'bumper': {
                'x': bumper.x,
                'y': bumper.y,
            }
        }
    )


async def notify_bumper_expired(game_id, bumper):
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f"pong_{game_id}",
        {
            'type': 'bumper_expired',
            'bumper': {
                'x': bumper.x,
                'y': bumper.y
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

    print(f"[collisions.py] Ball collided with {border_side} border at coor x = {ball.x}.")

async def notify_bumper_collision(game_id, bumper, ball):
    collision_info = {
        'type': 'bumper_collision',
        'bumper_x': bumper.x,
        'bumper_y': bumper.y,
        'new_speed_x': ball.speed_x,
        'new_speed_y': ball.speed_y,
    }
    await notify_collision(game_id, collision_info)



# --------- END GAME : NOTIFICATIONS  -----------

async def notify_game_finished(game_id, tournament_id, winner, looser):
    # Si winner et looser sont des objets CustomUser, on récupère leur username,
    # sinon on les laisse tels quels (cas d'un match en mode local, où ce sont déjà des chaînes)
    winner_serializable = winner.username if hasattr(winner, 'username') else winner
    looser_serializable = looser.username if hasattr(looser, 'username') else looser

    print(f"[broadcast.py] notify_game_finished winner: {winner_serializable} looser: {looser_serializable} tournament_id: {tournament_id}")
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f"pong_{game_id}",
        {
            'type': 'game_over',
            'tournament_id': str(tournament_id),
            'winner': winner_serializable,
            'looser': looser_serializable
        }
    )