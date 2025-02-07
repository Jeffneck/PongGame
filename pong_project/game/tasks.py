# # game/tasks.py

# import asyncio
# from .game_loop.loop import game_loop

# ACTIVE_GAMES = {}  # Dict: { game_id -> asyncio.Task }
# # print("[tasks.py] id(ACTIVE_GAMES) =", id(ACTIVE_GAMES))

# async def start_game_loop(game_id):

#     task = asyncio.create_task(game_loop(game_id))
#     # print(f"[start_game_loop] id(ACTIVE_GAMES)={id(ACTIVE_GAMES)} before storing")
#     ACTIVE_GAMES[str(game_id)] = task

#     print(f"[tasks.py] Game loop started for game_id={game_id}")

#     try:
#         await task
#     except asyncio.CancelledError:
#         print(f"[tasks.py] Game loop for game_id={game_id} was cancelled.")
#     finally:
#         del ACTIVE_GAMES[game_id]
#         print(f"[tasks.py] Game loop ended for game_id={game_id}")

# def is_game_running(game_id):
#     return game_id in ACTIVE_GAMES

# def stop_game(game_id):
#     print(f"[stop_game] id(ACTIVE_GAMES)={id(ACTIVE_GAMES)}")
#     task = ACTIVE_GAMES.get(str(game_id))
#     if task:
#         print(f"[stop_game] Annulation de la tâche pour game_id={game_id}")
#         task.cancel()
#         # print(f"[stop_game] Task pour game_id={game_id} annulée.")
#     else:
#         print(f"[stop_game] Aucune tâche trouvée pour game_id={game_id} !")

from game.game_loop.models_utils import set_gameSession_status


import asyncio

ACTIVE_GAMES = {}   # { game_id: main_task }
SUBTASKS = {}       # { game_id: set of subtasks }

async def start_game_loop(game_id):
    from .game_loop.loop import game_loop
    task = asyncio.create_task(game_loop(game_id))
    ACTIVE_GAMES[str(game_id)] = task
    SUBTASKS[str(game_id)] = set()  # Initialise le set pour les sous-tâches

    print(f"[tasks.py] Game loop started for game_id={game_id}")
    try:
        await task
    except asyncio.CancelledError:
        print(f"[tasks.py] Game loop for game_id={game_id} was cancelled.")
    finally:
        del ACTIVE_GAMES[str(game_id)]
        SUBTASKS.pop(str(game_id), None)
        print(f"[tasks.py] Game loop ended for game_id={game_id}")

def register_subtask(game_id, subtask):
    """Enregistre une sous-tâche pour le game_id."""
    if str(game_id) not in SUBTASKS:
        SUBTASKS[str(game_id)] = set()
    SUBTASKS[str(game_id)].add(subtask)

     # Option : cleanup dès que la tâche est terminée
    def _on_done(_):
        if game_id in SUBTASKS:
            SUBTASKS[str(game_id)].discard(subtask)

    subtask.add_done_callback(_on_done)

async def stop_game(game_id):
    """Annule la tâche principale ET toutes les sous-tâches associées."""
    # await set_gameSession_status(game_id, "cancelled")
    main_task = ACTIVE_GAMES.get(str(game_id))
    if main_task:
        main_task.cancel()
        print(f"[stop_game] Annulation de la tâche principale pour game_id={game_id}")
    # # Annuler toutes les sous-tâches
    # subtasks = SUBTASKS.get(str(game_id), [])
    # for st in subtasks:
    #     st.cancel()
    # Annule toutes les sous-tâches
    for st in SUBTASKS.get(str(game_id), []):
        st.cancel()

    SUBTASKS.pop(str(game_id), None)
    ACTIVE_GAMES.pop(str(game_id), None)
    #print(f"[stop_game] {len(subtasks)} sous-tâches annulées pour game_id={game_id}")