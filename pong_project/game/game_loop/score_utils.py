from channels.layers import get_channel_layer
from ..models import GameSession, GameResult
from .broadcast import notify_game_finished
from .redis_utils import set_key, get_key, scan_and_delete_keys
from asgiref.sync import sync_to_async

# transformer en parametre ajustable GameParameters?
WIN_SCORE = 4  

async def handle_score(game_id, scorer):
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

async def winner_detected(game_id):

    score_left = int(get_key(game_id, "score_left") or 0)
    score_right = int(get_key(game_id, "score_right") or 0)

    if (score_left == WIN_SCORE or score_right == WIN_SCORE):
        return True
    return False

async def finish_game(game_id, score_left, score_right):
    channel_layer = get_channel_layer()
    try:
        session = await sync_to_async(GameSession.objects.get)(pk=game_id)
        session.status = 'finished'
        await sync_to_async(session.save)()

        if score_left > score_right :
            winner = session.player_left
            looser = session.player_right
        else : 
            winner = session.player_right
            looser = session.player_left

        await sync_to_async(GameResult.objects.create)(
            game=session,
            winner=winner,
            looser=looser,
            score_left=score_left,
            score_right=score_right
        )
        print(f"[loop.py] GameResult created for game_id={game_id}, winner={winner}, looser{looser}")
    except GameSession.DoesNotExist:
        print(f"[loop.py] GameSession {game_id} does not exist.")
        pass

    # Notifier
    notify_game_finished(game_id, winner, looser)

    # Nettoyer les clés Redis
    await scan_and_delete_keys(game_id)
    print(f"[loop.py] Redis keys deleted for game_id={game_id}")