# game/tasks.py

import asyncio

ACTIVE_GAMES = {}  # dict: { game_id -> asyncio.Task }

async def start_game_loop(game_id):
    """
    Lance la game_loop(game_id), stocke la Task dans ACTIVE_GAMES.
    """
    from .game_loop import game_loop

    # Crée une nouvelle Task
    task = asyncio.create_task(game_loop(game_id))
    ACTIVE_GAMES[game_id] = task

    # Attend que la boucle se termine (score atteint ou session finished)
    await task

    # Une fois terminé, on enlève du dictionnaire
    del ACTIVE_GAMES[game_id]

def is_game_running(game_id):
    return (game_id in ACTIVE_GAMES)

def stop_game(game_id):
    """
    Permet de stopper manuellement une partie en cours (annuler la Task).
    """
    task = ACTIVE_GAMES.get(game_id)
    if task:
        task.cancel()
