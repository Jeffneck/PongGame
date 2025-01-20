# game/game_loop/powerups.py

import time
from .redis_utils import get_key
from .redis_macroutils import set_powerup_redis, delete_powerup_redis
from .broadcast import notify_powerup_applied, notify_powerup_spawned, notify_powerup_expired
import random
# -------------- POWER UP --------------------

async def handle_powerups(game_id, powerup_orbs, current_time, last_powerup_spawn_time, powerup_spawn_interval):
    if current_time - last_powerup_spawn_time >= powerup_spawn_interval:
        active_powerups = await count_active_powerups(game_id, powerup_orbs)
        if active_powerups < 2:  # MAX_ACTIVE_POWERUPS = 2
            powerup_orb = random.choice(powerup_orbs)
            if not powerup_orb.active:
                spawned = await spawn_powerup(game_id, powerup_orb)
                if spawned:
                    last_powerup_spawn_time = current_time
                    print(f"[game_loop.py] game_id={game_id} - PowerUp {powerup_orb.effect_type} spawned.")


async def spawn_powerup(game_id, powerup_orb, terrain_rect):
    # Ne pas faire spawn 2 fois le même powerup sur le terrain
    # if powerup_orb.active:
    #     print(f"[powerups.py] PowerUp {powerup_orb.effect_type} is already active, skipping spawn.")
    #     return False

    if await powerup_orb.spawn(terrain_rect):
        set_powerup_redis(game_id, powerup_orb)
        print(f"[powerups.py] PowerUp {powerup_orb.effect_type} spawned at ({powerup_orb.x}, {powerup_orb.y})")
        await notify_powerup_spawned(game_id, powerup_orb)
        return True
    return False

async def apply_powerup(game_id, player, powerup_orb, channel_layer):
    print(f"[powerups.py] Applying power-up {powerup_orb.effect_type} to {player}")
    delete_powerup_redis(game_id, powerup_orb)
    await notify_powerup_applied(game_id, player, powerup_orb.effect_type, channel_layer)

async def count_active_powerups(game_id, powerup_orbs):
    count = 0
    for powerup_orb in powerup_orbs:
        active = get_key(game_id, f"powerup_{powerup_orb.effect_type}_active")
        if active and active.decode('utf-8') == '1':
            count += 1
    print(f"[loop.py] count_active_powerups ({count})")
    return count

async def handle_powerup_expiration(game_id, powerup_orbs):
    current_time = time.time()
    for powerup_orb in powerup_orbs:
        if powerup_orb.active and current_time - powerup_orb.spawn_time >= powerup_orb.duration:
            delete_powerup_redis(game_id, powerup_orb)
            print(f"[game_loop.py] PowerUp {powerup_orb.effect_type} expired at ({powerup_orb.x}, {powerup_orb.y})")
            await notify_powerup_expired(game_id, powerup_orb)


# -------------- POWER UP : UPDATE REDIS DATA --------------------
async def set_powerup_redis(game_id, powerup_orb):
    powerup_orb.activate()
    set_key(game_id, f"powerup_{powerup_orb.effect_type}_active")
    set_key(game_id, f"powerup_{powerup_orb.effect_type}_x")
    set_key(game_id, f"powerup_{powerup_orb.effect_type}_y")

async def delete_powerup_redis(game_id, powerup_orb):
    powerup_orb.deactivate()
    delete_key(game_id, f"powerup_{powerup_orb.effect_type}_active")
    delete_key(game_id, f"powerup_{powerup_orb.effect_type}_x")
    delete_key(game_id, f"powerup_{powerup_orb.effect_type}_y")