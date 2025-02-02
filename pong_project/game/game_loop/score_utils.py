# game/game_loop/score_utils.py

from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async
from .broadcast import notify_game_finished
from .redis_utils import set_key, get_key, scan_and_delete_keys
from .models_utils import is_gameSession_Online, set_gameSession_status, create_gameResults, get_LocalTournament

# transformer en parametre ajustable GameParameters?
WIN_SCORE = 5 

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
    gameSession = await set_gameSession_status(game_id, "finished")
    if not gameSession:
        print(f"[finish_game] GameSession {game_id} does not exist.")
        return

    # Pour être sûr que les attributs player_left et player_right sont préchargés,
    # vérifiez qu'ils ne déclenchent pas de requête additionnelle.
    # Ici, ils ont été chargés grâce au select_related dans set_gameSession_status.

    # Si la GameSession est Online, créer un enregistrement des gameResults
    gameSession_isOnline = await is_gameSession_Online(game_id)
    if gameSession_isOnline:
        if score_left > score_right:
            winner = gameSession.player_left
            looser = gameSession.player_right
        else:
            winner = gameSession.player_right
            looser = gameSession.player_left

        endgame_infos = {
            'winner': winner,
            'looser': looser,
            'score_left': score_left,
            'score_right': score_right,
        }
        await create_gameResults(game_id, endgame_infos)
    else:
        # Pour une session locale
        if score_left > score_right:
            winner = gameSession.player_left_name
            looser = gameSession.player_right_name
        else:
            winner = gameSession.player_right_name
            looser = gameSession.player_left_name

    # Gestion du tournoi (inchangé)
    tournament = await get_LocalTournament(game_id, "semifinal1")
    if tournament:
        print(f"[finish_game] this game was semifinal1 from tournament game_id={game_id}")
        tournament.status = 'semifinal1_done'
        tournament.winner_semifinal_1 = winner
        await sync_to_async(tournament.save)()
    else:
        tournament = await get_LocalTournament(game_id, "semifinal2")
        if tournament:
            tournament.status = 'semifinal2_done'
            tournament.winner_semifinal_2 = winner
            await sync_to_async(tournament.save)()
        else:
            tournament = await get_LocalTournament(game_id, "final")
            if tournament:
                tournament.status = 'finished'
                await sync_to_async(tournament.save)()
            else:
                print(f"[finish_game] No tournament found for game_id={game_id}")

    tournament_id = gameSession.tournament_id
    print(f"[finish_game] tournament_id={tournament_id}")
    await notify_game_finished(game_id, tournament_id, winner, looser)
    scan_and_delete_keys(game_id)
    print(f"[loop.py] Redis keys deleted for game_id={game_id}")
