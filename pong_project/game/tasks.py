import asyncio

ACTIVE_GAMES = {}  # game_id -> asyncio.Task

async def start_game_loop(game_id):
    from .game_loop import game_loop
    task = asyncio.create_task(game_loop(game_id))
    ACTIVE_GAMES[game_id] = task
    await task
    # Quand la task se termine
    del ACTIVE_GAMES[game_id]

def is_game_running(game_id):
    return game_id in ACTIVE_GAMES

def stop_game(game_id):
    """
    Permet éventuellement de stopper manuellement la partie (annuler la Task).
    """
    task = ACTIVE_GAMES.get(game_id)
    if task:
        task.cancel()
        # On gérera la cleanup en exception
