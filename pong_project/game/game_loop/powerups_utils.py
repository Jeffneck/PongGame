import time
from .dimensions_utils import get_terrain_rect
from .redis_utils import set_key, get_key, delete_key
from .broadcast import notify_powerup_applied, notify_powerup_spawned, notify_powerup_expired
import asyncio
import math
import random
from game.tasks import register_subtask


MAX_ACTIVE_POWERUPS = 2
SPAWN_INTERVAL_POWERUPS = 8
DURATION_EFFECT_POWERUPS = 4

def get_active_objects(powerup_orbs, bumpers): # / added
    active_powerups = [orb for orb in powerup_orbs if orb.active]
    active_bumpers = [bumper for bumper in bumpers if bumper.active]
    print(f"[DEBUG] Currently active objects: {len(active_powerups)} powerups, {len(active_bumpers)} bumpers")
    
    # Print positions of all active objects
    for powerup in active_powerups:
        print(f"[DEBUG] Active powerup at ({powerup.x}, {powerup.y})")
    for bumper in active_bumpers:
        print(f"[DEBUG] Active bumper at ({bumper.x}, {bumper.y})")
    
    return active_powerups, active_bumpers

# -------------- POWER UP --------------------
async def handle_powerups_spawn(game_id, powerup_orbs, current_time, bumpers): # / modified
    # Initialisation de last_powerup_spawn_time si elle n'est pas déjà définie
    if not hasattr(handle_powerups_spawn, "last_powerup_spawn_time") or handle_powerups_spawn.last_powerup_spawn_time is None: # /modified
        handle_powerups_spawn.last_powerup_spawn_time = current_time # Initialisation lors du premier appel
        return

    # Utilisation de la variable statique pour vérifier l'intervalle de temps
    if current_time - handle_powerups_spawn.last_powerup_spawn_time >= SPAWN_INTERVAL_POWERUPS:
        # Get current active objects for debugging
        active_powerups, active_bumpers = get_active_objects(powerup_orbs, bumpers) # / added
        print(f"[DEBUG] Attempting powerup spawn with {len(active_powerups)} active powerups and {len(active_bumpers)} active bumpers")

        active_powerups = count_active_powerups(game_id, powerup_orbs)
        if active_powerups < MAX_ACTIVE_POWERUPS:
            # S'assurer qu'on ne génère qu'un seul powerup à la fois
            available_powerups = [orb for orb in powerup_orbs if not orb.check_cooldown() and not orb.active]
            if available_powerups:
                powerup_orb = random.choice(available_powerups)
                if not powerup_orb.active:
                    terrain = get_terrain_rect(game_id)
                    spawned = await spawn_powerup(game_id, powerup_orb, terrain, powerup_orbs, bumpers)
                    if spawned:
                        # Mettre à jour le temps de spawn du powerup pour éviter les doubles spawns
                        handle_powerups_spawn.last_powerup_spawn_time = current_time
                        print(f"[game_loop.py] game_id={game_id} - PowerUp {powerup_orb.effect_type} spawned.")



async def spawn_powerup(game_id, powerup_orb, terrain_rect, powerup_orbs, bumpers): # / modified
    # Ne pas faire spawn 2 fois le même powerup sur le terrain
    if powerup_orb.active:
        print(f"[powerups.py] PowerUp {powerup_orb.effect_type} is already active, skipping spawn.")
        return False

    if powerup_orb.spawn(terrain_rect, powerup_orbs, bumpers):
        set_powerup_redis(game_id, powerup_orb)
        print(f"[powerups.py] PowerUp {powerup_orb.effect_type} spawned at ({powerup_orb.x}, {powerup_orb.y})")
        await notify_powerup_spawned(game_id, powerup_orb)
        return True
    return False



async def apply_powerup(game_id, player, powerup_orb):
    print(f"[powerups.py] Applying power-up {powerup_orb.effect_type} to {player}")
    # Create task for handling effect duration
    subtask = asyncio.create_task(handle_powerup_duration(game_id, player, powerup_orb))
    register_subtask(game_id, subtask)
    print(f"[game_loop.py] Creating duration task for {powerup_orb.effect_type}")
    delete_powerup_redis(game_id, powerup_orb)
    await notify_powerup_applied(game_id, player, powerup_orb.effect_type, DURATION_EFFECT_POWERUPS)


async def handle_powerup_duration(game_id, player, powerup_orb): 
    """Handles the duration of a power-up effect asynchronously."""
    effect_type = powerup_orb.effect_type
    effect_duration = 5  # 5 seconds for all effects

    print(f"[game_loop.py] Starting effect {effect_type} for {player}")

    # Apply effect
    #IMPROVE => utiliser shown_size de paddle pour original_height
    

    print("handle_powerup_duration")
    if effect_type == 'flash':
        set_key(game_id, f"flash_effect", 1)
        try:
            await asyncio.sleep(0.3)
        except asyncio.CancelledError:
            print(f"[flash effect] => CANCELLED for game_id={game_id}")
            return
        #await asyncio.sleep(0.3) # Flash lasts 300ms

        delete_key(game_id, f"flash_effect")

    elif effect_type == 'shrink':
        opponent = 'left' if player == 'right' else 'right'
        print(f"[game_loop.py] Applying shrink to {opponent}")  # Debug log
        
        # Get current height and store it as original
        current_height = float(get_key(game_id, f"paddle_{opponent}_height") or 60)
        print(f"[game_loop.py] Original height: {current_height}")  # Debug log
        
        # Store original height for restoration
        set_key(game_id, f"paddle_{opponent}_original_height", current_height)
        
        # Calculate and set new height
        new_height = current_height * 0.5
        set_key(game_id, f"paddle_{opponent}_height", new_height)
        # print(f"[game_loop.py] New height set to: {new_height}")  # Debug log
        
        # Wait for duration
        try:
            await asyncio.sleep(effect_duration)
        except asyncio.CancelledError:
            return
    
        # Restore original height
        original_height = float(get_key(game_id, f"paddle_{opponent}_original_height") or 60)
        set_key(game_id, f"paddle_{opponent}_height", original_height)
        delete_key(game_id, f"paddle_{opponent}_original_height")
        # print(f"[game_loop.py] Height restored to: {original_height}")  # Debug log

    elif effect_type == 'speed':
        # Set paddle speed multiplier
        set_key(game_id, f"paddle_{player}_speed_boost", 1)  # Flag for speed boost
        # print(f"[game_loop.py] Speed boost applied to {player} paddle")
        
        try:
            await asyncio.sleep(effect_duration)
        except asyncio.CancelledError:
            return
        
        # Remove speed boost
        delete_key(game_id, f"paddle_{player}_speed_boost")
        # print(f"[game_loop.py] Speed boost removed from {player} paddle")

    elif effect_type == 'ice':
        opponent = 'left' if player == 'right' else 'right'
        set_key(game_id, f"paddle_{opponent}_ice_effect", 1)
        try:
            await asyncio.sleep(effect_duration)
        except asyncio.CancelledError:
            return
        delete_key(game_id, f"paddle_{opponent}_ice_effect")

    elif effect_type == 'sticky':
        set_key(game_id, f"paddle_{player}_sticky", 1)
        try:
            await asyncio.sleep(effect_duration)
        except asyncio.CancelledError:
            return
        delete_key(game_id, f"paddle_{player}_sticky")

    elif effect_type == 'invert':
        opponent = 'left' if player == 'right' else 'right'
        set_key(game_id, f"paddle_{opponent}_inverted", 1)
        try:
            await asyncio.sleep(effect_duration)
        except asyncio.CancelledError:
            return
        delete_key(game_id, f"paddle_{opponent}_inverted")
    print("END handle_powerup_duration")





def count_active_powerups(game_id, powerup_orbs):
    count = 0
    for powerup_orb in powerup_orbs:
        active = get_key(game_id, f"powerup_{powerup_orb.effect_type}_active") or 0
        if active and active.decode('utf-8') == '1':
            count += 1
    # print(f"[loop.py] count_active_powerups ({count})")
    return count

async def handle_powerup_expiration(game_id, powerup_orbs):
    current_time = time.time()
    for powerup_orb in powerup_orbs:
        if powerup_orb.active and current_time - powerup_orb.spawn_time >= powerup_orb.duration:
            powerup_orb.deactivate() # / added
            delete_powerup_redis(game_id, powerup_orb)
            print(f"[game_loop.py] PowerUp {powerup_orb.effect_type} expired at ({powerup_orb.x}, {powerup_orb.y})")
            await notify_powerup_expired(game_id, powerup_orb)


# -------------- POWER UP : UPDATE REDIS DATA --------------------
def set_powerup_redis(game_id, powerup_orb):
    powerup_orb.activate()
    set_key(game_id, f"powerup_{powerup_orb.effect_type}_active", 1)
    set_key(game_id, f"powerup_{powerup_orb.effect_type}_x", powerup_orb.x)
    set_key(game_id, f"powerup_{powerup_orb.effect_type}_y", powerup_orb.y)

def delete_powerup_redis(game_id, powerup_orb):
    powerup_orb.deactivate()
    delete_key(game_id, f"powerup_{powerup_orb.effect_type}_active")
    delete_key(game_id, f"powerup_{powerup_orb.effect_type}_x")
    delete_key(game_id, f"powerup_{powerup_orb.effect_type}_y")
