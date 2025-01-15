# game/manager.py

import asyncio
import sys
from .tasks import start_game_loop

_GLOBAL_LOOP = None

def set_global_loop(loop):
    """
    Stocke dans _GLOBAL_LOOP la référence à la loop 'principale'.
    Appelée au démarrage dans asgi.py
    """
    global _GLOBAL_LOOP
    _GLOBAL_LOOP = loop

def get_global_loop():
    return _GLOBAL_LOOP

def schedule_game(game_id):
    """
    Programme l'exécution de start_game_loop(game_id)
    sans bloquer la requête HTTP.
    """
    try:
        current_loop = asyncio.get_event_loop()  # event loop du thread courant
        current_loop.create_task(start_game_loop(game_id))
        print(f"[schedule_game] create_task OK dans loop={current_loop} pour game_id={game_id}")
    except RuntimeError:
        # => On est dans un thread sans event loop
        print("No current event loop in this thread, fallback run_coroutine_threadsafe", file=sys.stderr)

        global_loop = get_global_loop()
        if global_loop:
            asyncio.run_coroutine_threadsafe(start_game_loop(game_id), global_loop)
            print(f"[schedule_game] run_coroutine_threadsafe OK dans global_loop={global_loop} pour game_id={game_id}")
        else:
            print("No global loop available, game cannot be scheduled.", file=sys.stderr)
