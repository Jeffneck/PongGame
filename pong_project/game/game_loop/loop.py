import asyncio
from django.conf import settings
from channels.layers import get_channel_layer
from .models_utils import get_gameSession_status, get_gameSession_parameters
from .dimensions_utils import get_terrain_rect
from .initialize_game import initialize_game_objects, initialize_redis
from .score_utils import handle_score, winner_detected, finish_game
from .paddles_utils import move_paddles, update_paddles_redis 
from .bumpers_utils import handle_bumpers, handle_bumper_expiration
from .collisions import check_collisions
from .ball_utils import reset_ball, move_ball, update_ball_redis 
from .powerups_utils import handle_powerups, handle_powerup_expiration
from .broadcast import broadcast_game_state

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
        parameters = await get_gameSession_parameters(game_id)
        
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
            session_status = await get_gameSession_status(game_id)
            # print(f"[game_loop.py] game_id={game_id} - Session status: {session_status}")
            if session_status != 'running':
                print(f"[game_loop.py] game_id={game_id} is not running (status={session_status}), breaking loop.")
                break

            # Mettre à jour les positions des raquettes depuis Redis en fonction de la vélocité
            move_paddles(game_id, paddle_left, paddle_right)
            # Mettre a jour redis avec la nouvelle position des paddles (après le mouvement)
            await update_paddles_redis(game_id, paddle_left, paddle_right)
            # print(f"[game_loop.py] game_id={game_id} - Paddles positions updated from Redis.")

            # Mettre à jour la position de la balle (ancienne valeur + increment)
            move_ball(game_id, ball)
            await update_ball_redis(game_id, ball)
            # print(f"[game_loop.py] game_id={game_id} - Ball position updated to ({ball.x}, {ball.y})")

            # 3. Vérifier les collisions
            scorer = await check_collisions(game_id, paddle_left, paddle_right, ball, bumpers, powerup_orbs)
            if scorer in ['score_left', 'score_right']:
                await handle_score(game_id, scorer)
                if (await winner_detected(game_id)):
                    await finish_game(game_id)
                    break
                else:
                    await reset_ball(game_id, ball)

            # 4. Gérer les power-ups
            if parameters.bonus_malus_activation:
                await handle_powerups(game_id, powerup_orbs, current_time, last_powerup_spawn_time, powerup_spawn_interval)
                await handle_powerup_expiration(game_id, powerup_orbs)


            # 5. Gérer les bumpers
            if parameters.bumpers_activation:
                await handle_bumpers(game_id, bumpers, current_time, last_bumper_spawn_time, bumper_spawn_interval)
                await handle_bumper_expiration(game_id, bumpers)

            # 8. Broadcast l'état actuel du jeu
            await broadcast_game_state(game_id, channel_layer, paddle_left, paddle_right, ball, powerup_orbs, bumpers)
            # print(f"[game_loop.py] game_id={game_id} - Broadcasted game state.")

            # Attendre le prochain cycle
            await asyncio.sleep(dt)
    
    except Exception as e:
        print(f"[game_loop.py] game_id={game_id} encountered an exception: {e}")
    
    finally:
        print(f"[game_loop.py] game_id={game_id} loop ended.")