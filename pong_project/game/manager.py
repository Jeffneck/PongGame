# game/manager.py

import asyncio
from game.tasks import start_game_loop
import sys

_GLOBAL_LOOP = None

def set_global_loop(loop):
    global _GLOBAL_LOOP
    _GLOBAL_LOOP = loop
    print(f"[manager.py] Global loop set: {loop}")

def get_global_loop():
    return _GLOBAL_LOOP

def schedule_game(game_id):
    try:
        current_loop = asyncio.get_event_loop()
        if not current_loop.is_running():
            raise RuntimeError("Event loop is not running")
        current_loop.create_task(start_game_loop(game_id))
        print(f"[schedule_game] create_task OK dans loop={current_loop} pour game_id={game_id}")
    except (RuntimeError, AttributeError) as e:
        print("No current event loop in this thread, fallback run_coroutine_threadsafe", file=sys.stderr)
        global_loop = get_global_loop()
        if global_loop and global_loop.is_running():
            future = asyncio.run_coroutine_threadsafe(start_game_loop(game_id), global_loop)
            print(f"[schedule_game] run_coroutine_threadsafe OK dans global_loop={global_loop} pour game_id={game_id}")
        else:
            print("No global loop available or loop is not running, game cannot be scheduled.", file=sys.stderr)
