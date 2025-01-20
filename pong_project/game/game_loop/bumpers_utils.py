# game/game_loop/bumpers.py

import time
from .redis_utils import get_key, set_key, delete_key
from .broadcast import notify_bumper_spawned, notify_bumper_expired
import random
# -------------- BUMPERS --------------------
async def handle_bumpers(game_id, bumpers, current_time, last_bumper_spawn_time, bumper_spawn_interval):
    if current_time - last_bumper_spawn_time >= bumper_spawn_interval:
        active_bumpers = await count_active_bumpers(game_id, bumpers)
        if active_bumpers < 2:  # MAX_BUMPERS = 2
            bumper = random.choice(bumpers)
            if not bumper.active:
                spawned = await spawn_bumper(game_id, bumper)
                if spawned:
                    last_bumper_spawn_time = current_time
                    print(f"[game_loop.py] game_id={game_id} - Bumper spawned at ({bumper.x}, {bumper.y}).")

async def spawn_bumper(game_id, bumper, terrain_rect):
    if await bumper.spawn(terrain_rect):
        set_bumper_redis(game_id, bumper)
        print(f"[game_loop.py] Bumper spawned at ({bumper.x}, {bumper.y})")
        await notify_bumper_spawned(game_id, bumper)
        return True
    return False

async def count_active_bumpers(game_id, bumpers):
    count = 0
    for bumper in bumpers:
        active = get_key(game_id, f"bumper_{bumper.x}_{bumper.y}_active")
        if active and active.decode('utf-8') == '1':
            count += 1
    print(f"[loop.py] count_active_bumpers ({count})")
    return count

async def handle_bumper_expiration(game_id, bumpers):
    current_time = time.time()
    for bumper in bumpers:
        active = get_key(game_id, f"bumper_{bumper.x}_{bumper.y}_active")
        if active and active.decode('utf-8') == '1'and current_time - bumper.spawn_time >= bumper.duration:
            delete_bumper_redis(game_id, bumper)
            print(f"[loop.py] Bumper at ({bumper.x}, {bumper.y}) expired")
            await notify_bumper_expired(game_id, bumper)

# -------------- BUMPERS : UPDATE REDIS DATA --------------------
async def set_bumper_redis(game_id, bumper):
    bumper.activate()
    set_key(game_id, f"bumper_{bumper.x}_{bumper.y}_active")
    set_key(game_id, f"bumper_{bumper.x}_x", 0)
    set_key(game_id, f"bumper_{bumper.y}_x", 0)

async def delete_bumper_redis(game_id, bumper):
    bumper.deactivate()
    delete_key(game_id, f"bumper_{bumper.x}_{bumper.y}_active")
    delete_key(game_id, f"bumper_{bumper.x}_{bumper.y}_x")
    delete_key(game_id, f"bumper_{bumper.x}_{bumper.y}_y")