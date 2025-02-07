# game/game_loop/bumpers_utils.py

import time
from .redis_utils import get_key, set_key, delete_key
from .dimensions_utils import get_terrain_rect
from .broadcast import notify_bumper_spawned, notify_bumper_expired
from .powerups_utils import get_active_objects
import random

MAX_ACTIVE_BUMPERS = 3
SPAWN_INTERVAL_BUMPERS = 5
async def handle_bumpers_spawn(game_id, bumpers, current_time, powerup_orbs):
    # Initialisation de last_bumper_spawn_time si elle n'est pas déjà définie
    if not hasattr(handle_bumpers_spawn, "last_bumper_spawn_time") or handle_bumpers_spawn.last_bumper_spawn_time is None:
        handle_bumpers_spawn.last_bumper_spawn_time = current_time  # Initialisation lors du premier appel
        return
    # Utilisation de la variable statique pour vérifier l'intervalle de temps
    if current_time - handle_bumpers_spawn.last_bumper_spawn_time >= SPAWN_INTERVAL_BUMPERS:
        # Get current active objects for debugging
        active_powerups, active_bumpers = get_active_objects(powerup_orbs, bumpers)
        print(f"[DEBUG] Attempting bumper spawn with {len(active_powerups)} active powerups and {len(active_bumpers)} active bumpers")

        active_bumpers = count_active_bumpers(game_id, bumpers)
        if active_bumpers < MAX_ACTIVE_BUMPERS:
            # S'assurer qu'on ne génère qu'un seul bumper à la fois
            bumper = random.choice(bumpers)
            if not bumper.active:
                terrain = get_terrain_rect(game_id)
                spawned = await spawn_bumper(game_id, bumper, terrain, powerup_orbs, bumpers)
                if spawned:
                    # Mettre à jour le temps de spawn du bumper pour éviter les doubles spawns
                    handle_bumpers_spawn.last_bumper_spawn_time = current_time
                    print(f"[game_loop.py] game_id={game_id} - Bumper spawned at ({bumper.x}, {bumper.y}).")


async def spawn_bumper(game_id, bumper, terrain_rect, powerup_orbs, bumpers): # / modified
    if bumper.spawn(terrain_rect, powerup_orbs, bumpers):
        set_bumper_redis(game_id, bumper)
        print(f"[game_loop.py] Bumper spawned at ({bumper.x}, {bumper.y})")
        await notify_bumper_spawned(game_id, bumper)
        return True
    return False

def count_active_bumpers(game_id, bumpers):
    count = 0
    for bumper in bumpers:
        # active = int(get_key(game_id, f"bumper_{bumper.x}_{bumper.y}_active") or 0)
        active = get_key(game_id, f"bumper_{bumper.x}_{bumper.y}_active") or 0
        if active and active.decode('utf-8') == '1':
        # if active :
            count += 1
    print(f"[loop.py] count_active_bumpers ({count})")
    return count

async def handle_bumper_expiration(game_id, bumpers):
    current_time = time.time()
    for bumper in bumpers:
        active = get_key(game_id, f"bumper_{bumper.x}_{bumper.y}_active") or 0
        # active = int(get_key(game_id, f"bumper_{bumper.x}_{bumper.y}_active") or 0)
        if active and active.decode('utf-8') == '1'and current_time - bumper.spawn_time >= bumper.duration:
        # if active and current_time - bumper.spawn_time >= bumper.duration:
            delete_bumper_redis(game_id, bumper)
            print(f"[loop.py] Bumper at ({bumper.x}, {bumper.y}) expired")
            await notify_bumper_expired(game_id, bumper)

# -------------- BUMPERS : UPDATE REDIS DATA --------------------
def set_bumper_redis(game_id, bumper):
    bumper.activate()
    set_key(game_id, f"bumper_{bumper.x}_{bumper.y}_active", 1)
    set_key(game_id, f"bumper_{bumper.x}_{bumper.y}_x", bumper.x)
    set_key(game_id, f"bumper_{bumper.x}_{bumper.y}_y", bumper.y)


def delete_bumper_redis(game_id, bumper):
    bumper.deactivate()
    delete_key(game_id, f"bumper_{bumper.x}_{bumper.y}_active")
    delete_key(game_id, f"bumper_{bumper.x}_{bumper.y}_x")
    delete_key(game_id, f"bumper_{bumper.x}_{bumper.y}_y")