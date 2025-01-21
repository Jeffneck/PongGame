# game/game_loop/score_utils.py

from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async
from .broadcast import notify_game_finished
from .redis_utils import set_key, get_key, scan_and_delete_keys
from .models_utils import set_gameSession_as_finished, create_gameResults

# transformer en parametre ajustable GameParameters?
WIN_SCORE = 4  

def handle_score(game_id, scorer):
    if scorer == 'score_left':
        score_left = int(get_key(game_id, "score_left") or 0) + 1
        set_key(game_id, "score_left", score_left)
        print(f"[loop.py] Player Left scored. Score: {score_left} - {get_key(game_id, 'score_right')}")            

    else :
        score_right = int(get_key(game_id, "score_right") or 0) + 1
        set_key(game_id, "score_right", score_right)
        print(f"[loop.py] Player Right scored. Score: {get_key(game_id, 'score_left')} - {score_right}")

# async def check_end_conditions(game_id, quitter):
#     if(quitter): 
#         if(quitter == "player_left"): 
#             score_left = 0
#             score_right = WIN_SCORE
#         if(quitter == "player_right"): 
#             score_left = WIN_SCORE
#             score_right = 0
#     else :
#         score_left = int(get_key(game_id, "score_left") or 0)
#         score_right = int(get_key(game_id, "score_right") or 0)

#     if (score_left == WIN_SCORE or score_right == WIN_SCORE):
#         finish_game(game_id)
#         return True
#     return False

def winner_detected(game_id):

    score_left = int(get_key(game_id, "score_left") or 0)
    score_right = int(get_key(game_id, "score_right") or 0)

    if (score_left == WIN_SCORE or score_right == WIN_SCORE):
        return True
    return False

async def finish_game(game_id):
    # Récupérer les scores depuis Redis
    score_left = int(get_key(game_id, "score_left") or 0)
    score_right = int(get_key(game_id, "score_right") or 0)

    # Marquer la session comme terminée et récupérer ses informations
    gameSession = await set_gameSession_as_finished(game_id)
    if not gameSession:
        print(f"[finish_game] GameSession {game_id} does not exist.")
        return

    # Identifier le gagnant et le perdant
    if score_left > score_right:
        winner = gameSession.player_left
        looser = gameSession.player_right
    else:
        winner = gameSession.player_right
        looser = gameSession.player_left

    # Préparer les informations de fin de partie
    endgame_infos = {
        'winner': winner,
        'looser': looser,
        'score_left': score_left,
        'score_right': score_right,
    }

    # Créer un enregistrement des résultats
    await create_gameResults(game_id, endgame_infos)

    # Notifier les utilisateurs via WebSocket
    await notify_game_finished(game_id, winner, looser)

    # Nettoyer les clés Redis
    scan_and_delete_keys(game_id)
    print(f"[loop.py] Redis keys deleted for game_id={game_id}")