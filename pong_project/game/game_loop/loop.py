import asyncio
from django.conf import settings
from channels.layers import get_channel_layer
from .models import GameSession
from .models_utils import initialize_game_objects, get_game_status, get_game_parameters, move_paddles, handle_score, finish_game, 
from asgiref.sync import sync_to_async

import random
import time

async def game_loop(game_id):
    """
    Boucle principale pour UNE partie identifiée par game_id.
    Tourne ~60 fois/s tant que la partie est "running".
    """
    channel_layer = get_channel_layer()
    dt = 1/60
    print(f"[game_loop.py] Starting loop for game_id={game_id}.")

    try:
        # Récupérer les paramètres du jeu
        parameters = await get_game_parameters(game_id)
        
        # Initialiser les objets de jeu
        paddle_left, paddle_right, ball, powerup_orbs, bumpers = await initialize_game_objects(game_id, parameters)
        print(f"[game_loop.py] Game objects initialized for game_id={game_id}.")
        
        # Initialiser les positions et vélocités dans Redis
        await initialize_redis(game_id, paddle_left, paddle_right, ball, powerup_orbs, bumpers)
        print(f"[game_loop.py] Game objects positions initialized in Redis for game_id={game_id}.")
        
        last_powerup_spawn_time = time.time()
        powerup_spawn_interval = 10  # Adjust as needed

        last_bumper_spawn_time = time.time()
        bumper_spawn_interval = 15  # Adjust as needed

        while True:
            current_time = time.time()
            # print(f"[game_loop.py] game_id={game_id} - Loop iteration at {current_time}")

            # Vérifier si la partie est encore "running"
            session_status = await get_game_status(game_id)
            # print(f"[game_loop.py] game_id={game_id} - Session status: {session_status}")
            if session_status != 'running':
                print(f"[game_loop.py] game_id={game_id} is not running (status={session_status}), breaking loop.")
                break

            # 1. Mettre à jour les positions des raquettes depuis Redis en fonction de la vélocité
            move_paddles(game_id, paddle_left, paddle_right)
            await update_paddles_redis(game_id, paddle_left, paddle_right)
            # print(f"[game_loop.py] game_id={game_id} - Paddles positions updated from Redis.")

            # 2. Mettre à jour la position de la balle
            ball.move()
            await update_ball_redis(game_id, ball)
            # print(f"[game_loop.py] game_id={game_id} - Ball position updated to ({ball.x}, {ball.y})")

            # 3. Vérifier les collisions
            collision = await check_collisions(game_id, paddle_left, paddle_right, ball, bumpers, powerup_orbs)
            if collision in ['score_left', 'score_right']:
                await handle_score(game_id, collision)
                # print(f"[game_loop.py] game_id={game_id} - Handling score for {collision}")
                
                # Vérifier si quelqu'un a gagné
                score_left = int(r.get(f"{game_id}:score_left") or 0)
                score_right = int(r.get(f"{game_id}:score_right") or 0)
                if score_left >= WIN_SCORE or score_right >= WIN_SCORE:
                    # On arrête la boucle si la partie est terminée
                    break
                else:
                    # Personne n'a encore gagné,
                    # on réinitialise la balle pour continuer la partie
                    terrain_rect = await get_terrain_rect(game_id)
                    center_x = terrain_rect['left'] + terrain_rect['width'] // 2
                    center_y = terrain_rect['top'] + terrain_rect['height'] // 2
                    ball.reset(center_x, center_y, 4, 4)  # Vitesse X/Y à ajuster
                    await update_ball_redis(game_id, ball)
                    print(f"[game_loop.py] Ball reset to ({ball.x}, {ball.y}) with speed ({ball.speed_x}, {ball.speed_y})")

            # 4. Gérer les power-ups
            if parameters.bonus_malus_activation:
                if current_time - last_powerup_spawn_time >= powerup_spawn_interval:
                    # Tenter de spawn un power-up
                    active_powerups = await count_active_powerups(game_id, powerup_orbs)
                    # print(f"[game_loop.py] game_id={game_id} - Active power-ups: {active_powerups}")
                    if active_powerups < 2:  # MAX_ACTIVE_POWERUPS = 2
                        powerup_orb = random.choice(powerup_orbs)
                        if not powerup_orb.active:
                            spawned = await spawn_powerup(game_id, powerup_orb)
                            if spawned:
                                last_powerup_spawn_time = current_time
                                print(f"[game_loop.py] game_id={game_id} - PowerUp {powerup_orb.effect_type} spawned.")

            # 5. Gérer les bumpers
            if parameters.bumpers_activation:
                if current_time - last_bumper_spawn_time >= bumper_spawn_interval:
                    # Tenter de spawn un bumper
                    active_bumpers = await count_active_bumpers(game_id, bumpers)
                    # print(f"[game_loop.py] game_id={game_id} - Active bumpers: {active_bumpers}")
                    if active_bumpers < 2:  # MAX_BUMPERS = 2
                        bumper = random.choice(bumpers)
                        if not bumper.active:
                            spawned = await spawn_bumper(game_id, bumper)
                            if spawned:
                                last_bumper_spawn_time = current_time
                                print(f"[game_loop.py] game_id={game_id} - Bumper spawned at ({bumper.x}, {bumper.y}).")

            # 6. Gérer les power-ups expirés
            await handle_powerup_expiration(game_id, powerup_orbs)
            # print(f"[game_loop.py] game_id={game_id} - Handled power-up expiration.")

            # 7. Gérer les bumpers expirés
            await handle_bumper_expiration(game_id, bumpers)
            # print(f"[game_loop.py] game_id={game_id} - Handled bumper expiration.")

            # 8. Broadcast l'état actuel du jeu
            await broadcast_game_state(game_id, channel_layer, paddle_left, paddle_right, ball, powerup_orbs, bumpers)
            # print(f"[game_loop.py] game_id={game_id} - Broadcasted game state.")

            # Attendre le prochain cycle
            await asyncio.sleep(dt)
    
    except Exception as e:
        print(f"[game_loop.py] game_id={game_id} encountered an exception: {e}")
    
    finally:
        print(f"[game_loop.py] game_id={game_id} loop ended.")