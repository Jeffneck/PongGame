# game/game_loop/powerups.py

import random
import time
from .redis_utils import set_key, get_key, delete_key
from .broadcast import notify_powerup_applied, notify_powerup_spawned, notify_powerup_expired

async def spawn_powerup(game_id, powerup_orb, terrain_rect):
    if powerup_orb.active:
        print(f"[powerups.py] PowerUp {powerup_orb.effect_type} is already active, skipping spawn.")
        return False

    if await powerup_orb.spawn(terrain_rect):
        set_key(game_id, f"powerup_{powerup_orb.effect_type}_active", 1)
        set_key(game_id, f"powerup_{powerup_orb.effect_type}_x", powerup_orb.x)
        set_key(game_id, f"powerup_{powerup_orb.effect_type}_y", powerup_orb.y)
        print(f"[powerups.py] PowerUp {powerup_orb.effect_type} spawned at ({powerup_orb.x}, {powerup_orb.y})")
        await notify_powerup_spawned(game_id, powerup_orb)
        return True
    return False

async def apply_powerup(game_id, player, powerup_orb, channel_layer):
    print(f"[powerups.py] Applying power-up {powerup_orb.effect_type} to {player}")
    powerup_orb.deactivate()
    delete_key(game_id, f"powerup_{powerup_orb.effect_type}_active")
    delete_key(game_id, f"powerup_{powerup_orb.effect_type}_x")
    delete_key(game_id, f"powerup_{powerup_orb.effect_type}_y")

    await notify_powerup_applied(game_id, player, powerup_orb.effect_type, channel_layer)

async def handle_powerup_expiration(game_id, powerup_orbs):
    current_time = time.time()
    for powerup_orb in powerup_orbs:
        if powerup_orb.active and current_time - powerup_orb.spawn_time >= powerup_orb.duration:
            powerup_orb.deactivate()
            delete_key(game_id, f"powerup_{powerup_orb.effect_type}_active")
            delete_key(game_id, f"powerup_{powerup_orb.effect_type}_x")
            delete_key(game_id, f"powerup_{powerup_orb.effect_type}_y")
            print(f"[powerups.py] PowerUp {powerup_orb.effect_type} expired at ({powerup_orb.x}, {powerup_orb.y})")
            await notify_powerup_expired(game_id, powerup_orb)
