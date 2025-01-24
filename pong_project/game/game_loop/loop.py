# game/game_loop/loop.py

import asyncio
import time
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async

from .redis_utils import get_key
from .models_utils import get_gameSession_status, set_gameSession_status, get_gameSession_parameters
from .initialize_game import initialize_game_objects, initialize_redis
from .paddles_utils import move_paddles
from .ball_utils import move_ball, move_ball_sticky, reset_ball
from .collisions import (
    handle_scoring_or_paddle_collision,
    # make_paddle_sticky,
    handle_border_collisions,
    handle_bumper_collision,
    handle_powerup_collision
)
from .score_utils import handle_score, winner_detected, finish_game
from .bumpers_utils import handle_bumpers_spawn, handle_bumper_expiration
from .powerups_utils import handle_powerups_spawn, handle_powerup_expiration
from .broadcast import broadcast_game_state

async def game_loop(game_id):
    """
    Boucle principale pour UNE partie identifiée par game_id.
    Tourne ~60 fois/s tant que la partie n'est pas 'finished'.
    """
    channel_layer = get_channel_layer()
    dt = 1/60
    print(f"[game_loop.py] Starting loop for game_id={game_id}.")

    try:
        # Récupérer/charger les paramètres
        parameters = await get_gameSession_parameters(game_id)
        if not parameters:
            print(f"[game_loop] Pas de paramètres pour le game_id={game_id}, on quitte.")
            return

        # Construire les objets (raquettes, balle, powerups, bumpers)
        paddle_left, paddle_right, ball, powerup_orbs, bumpers = initialize_game_objects(game_id, parameters)
        initialize_redis(game_id, paddle_left, paddle_right, ball, parameters) # modified
        print(f"[game_loop] Game objects initialisés pour game_id={game_id}")

        # 1) Attendre que le statut devienne 'ready' (durée max 60s)
        timeout = 60
        start_time = time.time()

        while True:
            session_status = await get_gameSession_status(game_id)
            print(f"[game_loop] game_id={game_id} en attente du statut 'ready'. Actuel={session_status}")

            if session_status == 'ready':
                print(f"[game_loop] game_id={game_id} => statut 'ready' détecté. On lance le jeu.")
                break

            if time.time() - start_time > timeout:
                print(f"[game_loop] Timeout: la partie {game_id} n'est jamais passée en 'ready' après {timeout}s.")
                return  # On abandonne

            await asyncio.sleep(1)

        # 2) Passer en 'running' et faire la boucle ~60fps
        await set_gameSession_status(game_id, 'running')
        print(f"[game_loop] game_id={game_id} => statut 'running'. Début de la boucle.")

        while True:
            # Vérifier si la partie est encore 'running' ou si on l'a terminée
            session_status = await get_gameSession_status(game_id)
            if session_status != 'running':
                print(f"[game_loop] game_id={game_id} => statut={session_status}. Fin de la boucle.")
                break

            current_time = time.time()

            # 2.1 - Mouvements
            move_paddles(game_id, paddle_left, paddle_right)

            #creer fonction is_sticky dans powerup utils ou ball utils
            stuck_flag = get_key(game_id, "ball_stuck")
            if stuck_flag and stuck_flag.decode('utf-8') == '1':
                move_ball_sticky(game_id, paddle_left, paddle_right, ball)
            else :
                move_ball(game_id, ball)
            # print(f"1")#debug
            # 2.2 - Collisions
            await handle_border_collisions(game_id, ball)
            await handle_bumper_collision(game_id, ball, bumpers)
            await handle_powerup_collision(game_id, ball, powerup_orbs)
            # print(f"2")#debug

            # 2.3 - Paddles / Score
            scorer = await handle_scoring_or_paddle_collision(game_id, paddle_left, paddle_right, ball)
            if scorer in ['score_left', 'score_right']:
                handle_score(game_id, scorer)

                # Vérifier si on a un gagnant
                if winner_detected(game_id):
                    await finish_game(game_id)
                    break
                else:
                    # Sinon reset de la balle
                    reset_ball(game_id, ball)

            # print(f"3")#debug
            # 2.4 - Powerups & Bumpers
            if parameters.bonus_malus_activation:
                await handle_powerups_spawn(game_id, powerup_orbs, current_time)
                await handle_powerup_expiration(game_id, powerup_orbs)

            if parameters.bumpers_activation:
                await handle_bumpers_spawn(game_id, bumpers, current_time)
                await handle_bumper_expiration(game_id, bumpers)
            # print(f"4")#debug

            # 2.5 - Broadcast de l'état
            await broadcast_game_state(game_id, channel_layer, paddle_left, paddle_right, ball, powerup_orbs, bumpers)

            # print(f"5")#debug
            # 2.6 - Attendre ~16ms
            await asyncio.sleep(dt)

    except Exception as e:
        print(f"[game_loop] Exception pour game_id={game_id} : {e}")

    finally:
        print(f"[game_loop] Fin du game_loop pour game_id={game_id}.")