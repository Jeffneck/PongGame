# game/tasks.py

import asyncio

ACTIVE_GAMES = {}  # Dict: { game_id -> asyncio.Task }

async def start_game_loop(game_id):
    """
    Lance la game_loop(game_id) et stocke la Task dans ACTIVE_GAMES.
    """
    from .game_loop import game_loop

    # Créer une nouvelle Task
    task = asyncio.create_task(game_loop(game_id))
    ACTIVE_GAMES[game_id] = task

    print(f"[tasks.py] Game loop started for game_id={game_id}")

    try:
        # Attendre que la boucle se termine (score atteint ou session finished)
        await task
    except asyncio.CancelledError:
        print(f"[tasks.py] Game loop for game_id={game_id} was cancelled.")
    finally:
        # Une fois terminé ou annulé, enlever de ACTIVE_GAMES
        del ACTIVE_GAMES[game_id]
        print(f"[tasks.py] Game loop ended for game_id={game_id}")

def is_game_running(game_id):
    """
    Vérifie si une partie est en cours.
    """
    return game_id in ACTIVE_GAMES

def stop_game(game_id):
    """
    Permet de stopper manuellement une partie en cours (annuler la Task).
    """
    task = ACTIVE_GAMES.get(game_id)
    if task:
        task.cancel()
        print(f"[tasks.py] Game loop for game_id={game_id} has been cancelled.")
