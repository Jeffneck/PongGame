# game/tasks.py

import asyncio
from .game_loop.loop import game_loop

ACTIVE_GAMES = {}  # Dict: { game_id -> asyncio.Task }

async def start_game_loop(game_id):

    task = asyncio.create_task(game_loop(game_id))
    ACTIVE_GAMES[game_id] = task

    print(f"[tasks.py] Game loop started for game_id={game_id}")

    try:
        await task
    except asyncio.CancelledError:
        print(f"[tasks.py] Game loop for game_id={game_id} was cancelled.")
    finally:
        del ACTIVE_GAMES[game_id]
        print(f"[tasks.py] Game loop ended for game_id={game_id}")

def is_game_running(game_id):
    return game_id in ACTIVE_GAMES

def stop_game(game_id):
    task = ACTIVE_GAMES.get(game_id)
    if task:
        task.cancel()
        print(f"[tasks.py] Game loop for game_id={game_id} has been cancelled.")
