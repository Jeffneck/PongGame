# game/game_loop/loop.py


import asyncio
import time
from django.conf import settings
from channels.layers import get_channel_layer

from .redis_utils import get_key
from .models_utils import get_gameSession_status, get_gameSession, is_online_gameSession, get_gameSession_parameters, set_gameSession_status
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
from .score_utils import handle_score, winner_detected, finish_game, reset_all_objects
from .bumpers_utils import handle_bumpers_spawn, handle_bumper_expiration
from .powerups_utils import handle_powerups_spawn, handle_powerup_expiration
from .broadcast import broadcast_game_state, notify_countdown, notify_scored

class WaitForPlayersTimeout(Exception):
    """Exception levée lorsqu'un délai d'attente est dépassé avant que les joueurs ne soient prêts."""
    pass

async def wait_for_players(game_id):
    print(f"[game_loop.py] wait_for_players {game_id}.")
    timeout = 30  # Durée maximale d'attente en secondes.
    start_time = time.time()
    
    # Boucle d'attente pour vérifier si les joueurs sont prêts
    while time.time() - start_time < timeout:
        gs = await get_gameSession(game_id)
        if gs.ready_left and gs.ready_right:
            print(f"[game_loop.py] wait_for_players Everyone is READY {game_id}.")
            return True
        await asyncio.sleep(0.1)  # Petite pause pour éviter une boucle trop chargée
    
    # Si le timeout est dépassé, on lève une exception
    raise WaitForPlayersTimeout(f"Délai d'attente de {timeout} secondes dépassé pour game_id {game_id}.")


async def countdown_before_game(game_id):
    for countdown_nb in range(3, 0, -1):
        await notify_countdown(game_id, countdown_nb)
        await asyncio.sleep(1)

# async def scored(game_id, scorer):
#     await notify_scored(game_id, scorer)
#     await asyncio.sleep(1)

async def game_loop(game_id):
    """
    Boucle principale pour UNE partie identifiée par game_id.
    Tourne ~90 fois/s tant que la partie n'est pas 'finished'.
    """
    channel_layer = get_channel_layer()
    dt = 1/90
    print(f"[game_loop.py] Starting loop for game_id={game_id}.")
    try:
        await wait_for_players(game_id)
        # Récupérer/charger les paramètres
        parameters = await get_gameSession_parameters(game_id)


        # Construire les objets (raquettes, balle, powerups, bumpers)
        paddle_left, paddle_right, ball, powerup_orbs, bumpers = initialize_game_objects(game_id, parameters)
        initialize_redis(game_id, paddle_left, paddle_right, ball, parameters)
        await countdown_before_game(game_id)
        # print(f"[game_loop] Game objects initialisés pour game_id={game_id}")

        
        # await set_gameSession_status(game_id, "running")
        
        # 2) Lancer la boucle ~90fps 
        while True:
            
            try :
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
                    await reset_all_objects(game_id, powerup_orbs, bumpers) 
                    await notify_scored(game_id)
                    await asyncio.sleep(1.5)
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
                if parameters.bonus_enabled:
                    await handle_powerups_spawn(game_id, powerup_orbs, current_time, bumpers)
                    await handle_powerup_expiration(game_id, powerup_orbs)

                if parameters.obstacles_enabled:
                    await handle_bumpers_spawn(game_id, bumpers, current_time, powerup_orbs)
                    await handle_bumper_expiration(game_id, bumpers)
                # print(f"4")#debug
                # balle fixe apres un point
                # launch_ball_after_score(game_id, ball)
                # 2.5 - Broadcast de l'état
                await broadcast_game_state(game_id, channel_layer, paddle_left, paddle_right, ball, powerup_orbs, bumpers)

                # print(f"5")#debug
                # 2.6 - Attendre ~16ms
                await asyncio.sleep(dt)
            except asyncio.CancelledError:
                await set_gameSession_status(game_id, "cancelled")
                return

    except asyncio.CancelledError:
        print(f"[game_loop] => CANCELLED => on arrête la game {game_id}")
        # Vous pouvez forcer le statut "cancelled" si ce n’est pas déjà fait
        await set_gameSession_status(game_id, "cancelled")
        return  # On sort de la fonction
    
    except Exception as e:
        print(f"[game_loop] Exception pour game_id={game_id} : {e}")

    finally:
        print(f"[game_loop] Fin du game_loop pour game_id={game_id}.")